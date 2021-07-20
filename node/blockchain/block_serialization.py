'''
Created on Feb 14, 2021

@author: brett_wood
'''
import struct, codecs
from binascii import unhexlify, hexlify
from hashlib import sha256
from utilities import sqlUtils
import struct
from codecs import decode, encode
from utilities.serialization import deserialize_text, serialize_text
from node.blockchain.transaction_serialization import *
from node.blockchain.header_serialization import *

def serialize_block(
        header,
        serialized_transactions
        ):
    
    block = header
    transaction_count = len(serialized_transactions)
    
    for i in range(0, transaction_count):
        block = block + serialized_transactions[i]
        
    return block


def deserialize_block(block):
    
    header = deserialize_block_header(block)
    counter = header[8]
    counter_int = int.from_bytes(counter, byteorder='big')
    block_length = len(block)
    
    transactions = []

    while counter_int < block_length:
        transaction = deserialize_transaction(block, counter_int)
        counter_int = transaction[4]
        transactions.append(transaction)
    
    deserialized_block = []
    deserialized_block.append(header)
    deserialized_block.append(transactions)
    
    return deserialized_block


if __name__ == '__main__':
    
    block = '00010000000139f0f33e7b91a8b4677ca26d197c07bbfd2ed07b2e63727389bca78dfaf9e440f83bddd83d8ce63bcd654706ed62448e4ae4b9a73d824a8decde95f00060f72a591d0ffff0000a8eae3331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638123d212e000201013c75b4c2a69b3a86e13ac62705a6cf2d8a56d7d8b8d18bf846c621d62478fe060040ebff9ba202e4e182ed5d5fd685e4220279547ce2368f93a9453174def02b454d9c93667c18e65ed24968b181be63a38af117a3c0c5b59e7e94baf8c5b602f7d70101010054504f4c59474f4e28282d33392e3337352038372e373637312c2d33392e3337352038372e36323530382c2d34352038372e36323530382c2d34352038372e373637312c2d33392e3337352038372e37363731292940e3f2ecdefaa8e3f6652e8960dcca0d09d713fe255cbb5920c79e5dfe46f9447971cb2c76c7e6870ec9641924fa7a4ce7955bf911caf8be624cb21e4cfbcbfaf300000000000000000000000000000000000001000100010060504f4c59474f4e28282d37382e37352038302e34333731342c2d37382e37352038302e33303038382c2d38302e31353632352038302e33303038382c2d38302e31353632352038302e34333731342c2d37382e37352038302e3433373134292940351a334d094730fbfc0d98a285fd8d5698c636e62c9ba5c3b5edc376d55dfc94a503ff10d926590ffc44e3ac414309ede0806b6ce1e0a9cfae071e039816aa7f0000000000000000000000000000000000'    #block_bytes = hexlify(serialized_block).decode('utf-8')
    block_bytes = unhexlify(block)
    deserialized_block = deserialize_block(block_bytes)
    print(deserialized_block)
    print(deserialized_block[1][0])
    print(deserialized_block[1][1])
    print(deserialized_block[1])
    
    


    