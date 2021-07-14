'''
Created on Jul 12, 2021

@author: brett_wood
'''
from node.blockchain.validate_block import validateBlockHeader, validateTransactions
from binascii import unhexlify, hexlify
from mining import findValidHeader
from datetime import datetime
from node.blockchain.header_operations import *
from create_landbase_transaction import getLandbaseTransaction
from utilities.hashing import calculateMerkleRoot
from node.blockchain.block_serialization import *
from node.blockchain.block_operations import addBlock
from node.blockchain.global_variables import bitland_version
from system_variables import block_height_url

def mineForLand():
    
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
    
    serialized_block = serialize_block(header, transactions)
    block_hex = hexlify(serialized_block).decode('utf-8')
    
    return block_hex


if __name__ == '__main__':

    block = mineForLand()
    print(block)
