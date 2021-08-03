'''
Created on Nov 9, 2020

@author: brett_wood
'''
import requests
import codecs
from hashlib import sha256
from binascii import unhexlify, hexlify
from datetime import datetime
from utilities.hashing import (
    calculateHeaderHash,
    calculateMerkleRoot
    )
from utilities.difficulty import (
    get_target_from_bits,
    get_bits_current_block
    )
from utilities.serialization import deserialize_text, serialize_text
from node.information.blocks import getMaxBlockHeight
from node.networking.node_update_functions import queue_new_block_from_peer
from mining.create_landbase_transaction import getLandbaseTransaction
from system_variables import block_height_url
from node.blockchain.header_operations import getPrevBlock
from node.blockchain.block_serialization import serialize_block
from node.blockchain.global_variables import bitland_version
from utilities.sqlUtils import (
    executeSql,
    executeSqlMultipleRows
    )
from node.blockchain.validate_block import validateTransactions
from node.blockchain.transaction_serialization import deserialize_transaction
import threading
from node.blockchain.block_adding_queueing import validateAddBlock
from node.blockchain.header_serialization import serializeMinerAddress

#UPDATE - give ability to pull these from a node rather than inside the code

def findValidHeader(
        version_byte,
        prev_block_byte, 
        mrkl_root_byte,
        time_byte,
        bits_byte,
        bitcoin_height_byte,
        miner_bitcoin_address_byte,
        start_nonce_byte,
        current_block_height
    ):

    difficulty_byte = get_target_from_bits(bits_byte)
    miner_bitcoin_address_full_byte = serializeMinerAddress(miner_bitcoin_address_byte)
   
    nonce_byte = start_nonce_byte
    nonce = int.from_bytes(nonce_byte,'big')

    header_byte_no_nonce = (version_byte + prev_block_byte + mrkl_root_byte + time_byte + bits_byte + bitcoin_height_byte + miner_bitcoin_address_full_byte )
    print()
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
        if(nonce > 4000000000):
            header_byte = b''
            status = 'timed out'
            break
        nonce_hex = hexlify(nonce_byte)
        status = 'found valid block'
        new_block_height = current_block_height + 1

    end_time = datetime.now()
    print(end_time - start_time)
    print(int.from_bytes(time_byte,'big'))
    
    return (header_byte, status,new_block_height)


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
            transaction_serialized_list.append(deserialize_transaction(unhexlify(mempool_transactions[i][0])))
        
        print(transaction_serialized_list)
        valid_transactions = validateTransactions(transactions=transaction_serialized_list)
        
        print(valid_transactions)
        
        if valid_transactions[0] != True:
            transaction_byte_list = []
    
    return transaction_byte_list


#UPDATE figure out if node is synching before starting to try to mine
def mining_process():
    
    mempool_transactions = validateMempoolTransactions()
    print(mempool_transactions)
    transactions = mempool_transactions
    print(transactions)
    
    landbase_transaction_bytes = getLandbaseTransaction()
    transactions.append(landbase_transaction_bytes)

    print(transactions)
    
    version = bitland_version
    time_ = int(round(datetime.utcnow().timestamp(),0))
    start_nonce = 0
    bitcoin_height = int(requests.get(block_height_url).text)
    miner_bitcoin_address = '6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b7773'
    
    version_bytes = version.to_bytes(2, byteorder = 'big')
    prev_block_bytes = getPrevBlock()
    mrkl_root_bytes = calculateMerkleRoot(transactions)
    time_bytes = time_.to_bytes(5, byteorder = 'big')
    bits_bytes = get_bits_current_block() 
    bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
    miner_bitcoin_address_bytes = unhexlify(miner_bitcoin_address)
    start_nonce_bytes = start_nonce.to_bytes(4, byteorder = 'big')    
    
    current_block_height = getMaxBlockHeight()
    
    print('entering mine')
    
    mine = findValidHeader(
        version_bytes,
        prev_block_bytes, 
        mrkl_root_bytes,
        time_bytes,
        bits_bytes,
        bitcoin_height_bytes,
        miner_bitcoin_address_bytes,
        start_nonce_bytes,
        current_block_height
    )
    
    header = mine[0]
    status = mine[1]
    block_height = mine[2]
    
    print('mining status: ' + status)
    
    #UPDATE do we need to wait at all to allow block to propagate?
    if status == 'found valid block':
        serialized_block = serialize_block(header, transactions)
        block_hex = hexlify(serialized_block).decode('utf-8')
        print(block_hex)
        
        t1 = threading.Thread(target=validateAddBlock,args=(serialized_block,),daemon=True)
        t1.start()
        t1.join()
    
    return mining_process()
            
        
if __name__ == '__main__':
    
    x = mining_process();

    
    
    
    
    
    