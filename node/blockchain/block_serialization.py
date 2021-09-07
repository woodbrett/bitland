'''
Created on Feb 14, 2021

@author: brett_wood
'''
from binascii import unhexlify, hexlify
from hashlib import sha256
from utilities import sql_utils
from codecs import decode, encode
from utilities.serialization import deserialize_text, serialize_text
from node.blockchain.transaction_serialization import *
from node.blockchain.header_serialization import *

def serializeBlock(
        header,
        serialized_transactions
        ):
    
    block = header
    transaction_count = len(serialized_transactions)
    
    for i in range(0, transaction_count):
        block = block + serialized_transactions[i]
        
    return block


def deserializeBlock(block):
    
    header = deserializeBlockHeader(block)
    counter = header.get('counter_bytes')
    counter_int = int.from_bytes(counter, byteorder='big')
    block_length = len(block)
    
    transactions = []

    while counter_int < block_length:
        transaction = deserializeTransaction(block, counter_int)
        counter_int = transaction[4]
        transactions.append(transaction)
    
    deserialized_block = []
    deserialized_block.append(header)
    deserialized_block.append(transactions)
    
    return deserialized_block



    