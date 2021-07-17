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
   
    nonce_byte = start_nonce_byte
    nonce = int.from_bytes(nonce_byte,'big')

    header_byte_no_nonce = (version_byte + prev_block_byte + mrkl_root_byte + time_byte + bits_byte + bitcoin_height_byte + miner_bitcoin_address_byte )
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
            print("nonce: " + str(nonce))
            print(datetime.now() - start_time)
            print(hexlify(header_byte).decode('utf-8'))
            print(hexlify(headerhash_byte).decode('utf-8'))
            print(str(current_block_height) + ' ' + str(getMaxBlockHeight()))
            if current_block_height != getMaxBlockHeight():
                header_byte = b''
                status = 'rival found block'
                break
        if(nonce > 2000000000):
            header_byte = b''
            status = 'timed out'
            break
        nonce_hex = hexlify(nonce_byte)
        status = 'found valid block'
        new_block_height = current_block_height + 1

    print(hexlify(header_byte).decode('utf-8'))
    
    end_time = datetime.now()
    print(end_time - start_time)
    print(int.from_bytes(time_byte,'big'))
    
    return (header_byte, status,new_block_height)
        

#UPDATE add transactions into this
def mining_process():
    
    transaction_1_bytes = getLandbaseTransaction()
    transactions = [transaction_1_bytes]
    
    version = bitland_version
    time_ = int(round(datetime.utcnow().timestamp(),0))
    start_nonce = 0
    bitcoin_height = int(requests.get(block_height_url).text)
    miner_bitcoin_address = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
    
    version_bytes = version.to_bytes(2, byteorder = 'big')
    prev_block_bytes = getPrevBlock()
    mrkl_root_bytes = calculateMerkleRoot(transactions)
    time_bytes = time_.to_bytes(5, byteorder = 'big')
    bits_bytes = get_bits_current_block() 
    bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
    miner_bitcoin_address_bytes = hexlify(miner_bitcoin_address.encode('utf-8'))
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
        queue_new_block_from_peer(block_height,block_hex)
    
    return mining_process()
            
        
if __name__ == '__main__':
    
    x = mining_process();
    
    
    '''
    transaction_1 = '000100010133504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c30203930292940ea032a860b9b4cc136ca208e14865839bb300a76237d816f45c587ae37a01355577aebbb4f810ba062ef1352b25feb62257d86f59f967e4c8587c867a3756afa0000'
    transaction_1_bytes = unhexlify(transaction_1)
    transaction_set_bytes = [transaction_1_bytes]

    merkle_root = calculateMerkleRoot(transaction_set_bytes) 
    print(merkle_root)   
    print(hexlify(merkle_root))  
    print(hexlify(merkle_root).decode('utf-8'))
    
    version = 1
    prev_block = '0000000000000000000000000000000000000000000000000000000000000000'
    #mrkl_root = merkle_root
    time_ = int(round(datetime.utcnow().timestamp(),0))
    bits = 0x1d0ffff0 
    bitcoin_height = 671842
    miner_bitcoin_address = '31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668'
    start_nonce = 0
    
    version_bytes = version.to_bytes(2, byteorder = 'big')
    prev_block_bytes = unhexlify(prev_block)
    mrkl_root_bytes = merkle_root
    time_bytes = time_.to_bytes(5, byteorder = 'big')
    bits_bytes = get_bits_current_block()
    bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
    miner_bitcoin_address_bytes = unhexlify(miner_bitcoin_address)
    start_nonce_bytes = start_nonce.to_bytes(4, byteorder = 'big')    
    
    
    header = findValidHeader(
        version_bytes,
        prev_block_bytes, 
        mrkl_root_bytes,
        time_bytes,
        bits_bytes,
        bitcoin_height_bytes,
        miner_bitcoin_address_bytes,
        start_nonce_bytes
        )
    
    print(header)
    
    print('000000000ffff000000000000000000000000000000000000000000000000000' > '00000000ffff0000000000000000000000000000000000000000000000000000')
    print('0000000ffff00000000000000000000000000000000000000000000000000000' > '00000000ffff0000000000000000000000000000000000000000000000000000')
    
    #'0ffff00000000000000000000000000000000000000000000000000000000000' 3
    #'00ffff0000000000000000000000000000000000000000000000000000000000' 109 - 0:00.000995
    #'000ffff000000000000000000000000000000000000000000000000000000000' 3538 - 0:00.010970
    #'0000ffff00000000000000000000000000000000000000000000000000000000' 34,254 - 0:00.085773
    #'00000ffff0000000000000000000000000000000000000000000000000000000' 2,244,265 - 0:05
    #'000000ffff000000000000000000000000000000000000000000000000000000' 26,126,655 - 1:09
    #'0000000ffff00000000000000000000000000000000000000000000000000000' 356,511,692 - 16:47
    #'00000000ffff0000000000000000000000000000000000000000000000000000' 500,000,000?? #original
    
    difficulty = '0000000ffff00000000000000000000000000000000000000000000000000000'
    '''