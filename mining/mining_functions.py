'''
Created on Nov 9, 2020

@author: brett_wood
'''
import requests
import codecs
from hashlib import sha256
from binascii import unhexlify, hexlify
from datetime import datetime, timezone
from utilities.hashing import (
    calculateHeaderHash,
    calculateMerkleRoot
    )
from utilities.difficulty import (
    getTargetFromBits,
    getBitsCurrentBlock
    )
from utilities.serialization import deserialize_text, serialize_text
from node.information.blocks import getMaxBlockHeight
from node.networking.node_update_functions import queueNewBlockFromPeer,\
    queueNewTransactionFromPeer
from mining.create_landbase_transaction import getLandbaseTransaction
from system_variables import block_height_url
from node.blockchain.header_operations import getPrevBlockGuarded,\
    calculateMerkleRoot64BitcoinBlocks
from node.blockchain.block_serialization import serializeBlock
from node.blockchain.global_variables import bitland_version
from utilities.sql_utils import (
    executeSql,
    executeSqlMultipleRows
    )
from node.blockchain.validate_block import validateTransactions
from node.blockchain.transaction_serialization import deserializeTransaction
import threading
from node.blockchain.block_adding_queueing import validateAddBlock
from node.blockchain.header_serialization import serializeMinerAddress
from utilities.bitcoin.bitcoin_requests import (
    getCurrentBitcoinBlockHeight,
    getBestBlockHash, 
    getBlockHeightFromHash
    )
from utilities.time_utils import getTimeNowSeconds
import time
from node.processing.synching import getNodeStatus

def findValidHeader(
        version_byte,
        prev_block_byte, 
        mrkl_root_byte,
        time_byte,
        bits_byte,
        bitcoin_hash_byte,
        bitcoin_height_byte,
        bitcoin_last_64_mrkl_byte,
        miner_bitcoin_address_byte,
        start_nonce_byte,
        current_block_height
    ):

    difficulty_byte = getTargetFromBits(bits_byte)
    miner_bitcoin_address_full_byte = serializeMinerAddress(miner_bitcoin_address_byte)
   
    nonce_byte = start_nonce_byte
    nonce = int.from_bytes(nonce_byte,'big')

    header_byte_no_nonce = (version_byte + prev_block_byte + mrkl_root_byte + time_byte + bits_byte + bitcoin_hash_byte + bitcoin_height_byte + bitcoin_last_64_mrkl_byte + miner_bitcoin_address_full_byte )
    header_byte = (header_byte_no_nonce + nonce_byte) 
    headerhash_byte = sha256(sha256(header_byte).digest()).digest()  
    
    print(headerhash_byte > difficulty_byte)
    
    start_time = datetime.now()
    status = 'running'
    new_block_height = 0
    
    while headerhash_byte > difficulty_byte:
        nonce = nonce + 1
        nonce_byte = nonce.to_bytes(4, byteorder = 'big')
        header_byte = (header_byte_no_nonce + nonce_byte) 
        headerhash_byte = sha256(sha256(header_byte).digest()).digest()  
        #print(hexlify(headerhash_byte).decode("utf-8"))
        if(nonce % 1000000 == 0):
            print("block: " + str(current_block_height) + "; nonce: " + str(nonce) + "; time: " + str(datetime.now() - start_time))
            if current_block_height != getMaxBlockHeight():
                header_byte = b''
                status = 'rival found block'
                break
        if(nonce % 10000000 == 0):
            node_status = getNodeStatus()
            node_connectivity = node_status.get('node_connectivity')    
            node_synched = node_status.get('node_synched')
            if node_synched == False or node_connectivity == False:
                print('node out of synch, exiting mine')
                status = 'node out of synch, exiting mine'
                break
        if(nonce > 4000000000):
            header_byte = b''
            status = 'timed out'
            break
    
    if headerhash_byte <= difficulty_byte:
        nonce_hex = hexlify(nonce_byte)
        status = 'found valid block'
        new_block_height = current_block_height + 1

    end_time = datetime.now()
    print(end_time - start_time)
    print(int.from_bytes(time_byte,'big'))
    
    return {
        'header_byte': header_byte, 
        'status': status,
        'new_block_height': new_block_height or 0
        }


def getTransactionsFromMempool(max_size_bytes=4000000):
    
    query = (
        "WITH RECURSIVE i AS ( " +
       "SELECT *, row_number() OVER (ORDER BY miner_fee_sats desc) AS rn " +
       "FROM bitland.transaction_mempool " +
       ") " +
       ", r AS ( " +
       "SELECT i.transaction_serialized, id, byte_size, byte_size AS byte_size_total, 2 AS rn " +
       "FROM   i " +
       "WHERE  rn = 1 " +
       "UNION ALL " +
       "SELECT i.transaction_serialized, i.id, i.byte_size, r.byte_size_total + i.byte_size, r.rn + 1 " +
       "FROM   r " +
       "JOIN   i USING (rn) " +
       "WHERE  r.byte_size_total < " + str(max_size_bytes) +
       ")" +
       "SELECT transaction_serialized " +
       "FROM   r;" 
    )
    
    try:
        transactions = executeSqlMultipleRows(query)
    
    except Exception as error:
        print("no transactions to include")
        transactions = 'no transactions to include'
        
    return transactions


#UPDATE this to throw out individual bad transactions rather than get rid of the whole thing
def validateMempoolTransactions():

    mempool_transactions = getTransactionsFromMempool()
    
    transaction_byte_list = []
    transaction_serialized_list = []
    
    if mempool_transactions != "no transactions to include":
        
        print(len(mempool_transactions))
        for i in range(0,len(mempool_transactions)):
            transaction_byte_list.append(unhexlify(mempool_transactions[i][0]))
            transaction_serialized_list.append(deserializeTransaction(unhexlify(mempool_transactions[i][0])))
        
        print(transaction_serialized_list)
        valid_transactions = validateTransactions(transactions=transaction_serialized_list)
        
        print(valid_transactions)
        
        if valid_transactions[0] != True:
            transaction_byte_list = []
    
    return transaction_byte_list


#UPDATE figure out if node is synching before starting to try to mine
def miningProcess():
    
    try:
        node_connectivity = False        
        node_synched = False
        while node_synched == False or node_connectivity == False:
            node_status = getNodeStatus()
            node_connectivity = node_status.get('node_connectivity')    
            node_synched = node_status.get('node_synched')
            if node_synched == False or node_connectivity == False:
                print('node not ready, waiting to set up mining')
                time.sleep(1)
        
        #create transaction set
        mempool_transactions = validateMempoolTransactions()
        print(mempool_transactions)
        transactions = mempool_transactions
        print(transactions)
        
        landbase_transaction_bytes = getLandbaseTransaction()
        transactions.append(landbase_transaction_bytes)
        print(transactions)
    
        #create header    
        version = bitland_version
        time_ = getTimeNowSeconds()
        start_nonce = 0
        bitcoin_hash = getBestBlockHash()
        bitcoin_height = getBlockHeightFromHash(bitcoin_hash)
        miner_bitcoin_address = '3N6E2nprHmWCk39ibj3nwMSF5J34eRupNb'
        
        version_bytes = version.to_bytes(2, byteorder = 'big')
        prev_block_bytes = getPrevBlockGuarded()
        mrkl_root_bytes = calculateMerkleRoot(transactions)
        time_bytes = time_.to_bytes(5, byteorder = 'big')
        bits_bytes = getBitsCurrentBlock() 
        bitcoin_hash_bytes = unhexlify(bitcoin_hash)
        bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
        bitcoin_last_64_mrkl_bytes = calculateMerkleRoot64BitcoinBlocks(block_height=bitcoin_height)
        miner_bitcoin_address_bytes = miner_bitcoin_address.encode('utf-8')
        start_nonce_bytes = start_nonce.to_bytes(4, byteorder = 'big')    
        
        current_block_height = getMaxBlockHeight()
        
        print('entering mine')
        
        mine = findValidHeader(
            version_bytes,
            prev_block_bytes, 
            mrkl_root_bytes,
            time_bytes,
            bits_bytes,
            bitcoin_hash_bytes,
            bitcoin_height_bytes,
            bitcoin_last_64_mrkl_bytes,
            miner_bitcoin_address_bytes,
            start_nonce_bytes,
            current_block_height
        )
        
        header = mine.get('header_byte')
        status = mine.get('status')
        block_height = mine.get('new_block_height')
        
        print('mining status: ' + status)
        
        #UPDATE do we need to wait at all to allow block to propagate?
        if status == 'found valid block':
            serialized_block = serializeBlock(header, transactions)
            block_hex = hexlify(serialized_block).decode('utf-8')
            print(block_hex)
            
            #t1 = threading.Thread(target=validateAddBlock,args=(serialized_block,),daemon=True)
            #t1.start()
            #t1.join()
            
            queueNewBlockFromPeer(current_block_height+1, block=block_hex)
    
    except:
        print("error starting mining, waiting 2 minutes")
        time.sleep(120) 
        
    return miningProcess()
        

if __name__ == "__main__":

    print(int(round(datetime.now(timezone.utc).timestamp(),0)))
    
    