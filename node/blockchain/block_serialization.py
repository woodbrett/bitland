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
from bitcoin.blocks import serialize_header

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
    
    block = '00010000000000000000000000000000000000000000000000000000000000000000b7628deb1d1ef8cb5a06c921483dd75710e5680e08d879da69aadc5317f29c5700604edc501d0ffff0000a4b5d333133353465373735353662373435613734333436623537346434633731346233353531346337323738343134643531363137303739363534363738343136393336363802953b0d0001000100010033504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c3020393029294004943558f144f57654898d441ade1e4a198a3a9c72da9b8b25d6e2196f9e6522c44641fd87a3136f636e0cd8f1793eb2f75ae8b3d8c04e502b1e36ac0af284810000000000000000000000000000000000'    #block_bytes = hexlify(serialized_block).decode('utf-8')
    block_bytes = unhexlify(block)
    deserialized_block = deserialize_block(block_bytes)
    print(deserialized_block)
    print(deserialized_block[1][0])
    print(deserialized_block[1][1])
    
    
    header = '0001000000000000000000000000000000000000000000000000000000000000000077aa69cd7e9566fbedeb1910ded5f0f6440839d94727b7cf42dac5bc35f5658000603ad5821d0ffff0000a42d431354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680131dd16'
    landbase_transaction = '0001000101010033504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c3020393029298038376333323339306138643631356634366564616361373133356234313939356138623138643532343664313231383762613763376563363532356435376139663639313461346161643466373530653230646535643530383439326366363338636530653631393939333364626131626664663630653266646236306466310000000000000000000000000000000000'
    transaction_2 = '0002020189475fa839c308f2c52f7c088037544709a7075e9de1e7f16e47077ed824d6450040d31c42f309a1e6742fe7efda401658f69221cb2ceec3fb8deb1ebe7db2117859a41ac4eb7a196cad3a3ddadacaccce4b9d967f7f60a839367a17628003a773970389475fa839c308f2c52f7c088037544709a7075e9de1e7f16e47077ed824d6450000030101005f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e3431382929408a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d6160201005f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e3431382929408a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d6160301005f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e3431382929408a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d61600174876e80032a001d1a94a200003e82a626331713435776e7364336132727a38346a6370323075363379343877346672646368616c3677737378'
    
    header_bytes = unhexlify(header)
    landbase_transaction_bytes = unhexlify(landbase_transaction)
    transaction_2_bytes = unhexlify(transaction_2)
    
    block_serialized = serialize_block(header_bytes, [landbase_transaction_bytes,transaction_2_bytes])

    