'''
Created on Dec 23, 2020

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
from node.blockchain.queries import *
import struct, codecs
from binascii import unhexlify, hexlify
from hashlib import sha256
import requests
from system_variables import block_height_url
from node.blockchain.global_variables import (
    bitcoin_block_range
    )
from utilities.difficulty import get_bits_current_block
import base58
from utilities.serialization import deserialize_text, serialize_text
from utilities.hashing import * 
from datetime import datetime
import time
from utilities.difficulty import get_target_from_bits
from utilities.bitcoin_requests import *
from node.blockchain.global_variables import *
from node.blockchain.header_serialization import serialize_block_header_utf8

def validateVer(version):
    
    version_int = int.from_bytes(version, byteorder='big')
    is_valid = version_int == 1
    
    return is_valid
    
def validatePrevBlock(prev_block, prev_block_input):
        
    is_valid = prev_block_input == prev_block
    return is_valid  


def getPrevBlock():
    
    if getBlockCount() == 0:
        node_prev_block = genesis_prev_block
    
    else:
        node_prev_block_hex = queryGetPrevBlock()
        node_prev_block = unhexlify(node_prev_block_hex)
    
    return node_prev_block  
    
    
def validateMrklRoot(mrkl_root, transactions):
    
    calculated_mrkl_root = calculateMerkleRoot(transactions)
    
    is_valid = calculated_mrkl_root == mrkl_root
        
    return is_valid


def validateTime(time_,realtime_validation=True):
    
    if getBlockCount() == 0:
    #skip this validation if first block
        is_valid = True
        return is_valid
    
    else:
        average_time_last_11 = getMedianBlockTime11()
    
        #UPDATE to connect to nodes
        network_adjusted_time = datetime.utcnow().timestamp()
        time_int = int.from_bytes(time_, byteorder='big')
        
        if realtime_validation==True:
            is_valid = (time_int > average_time_last_11 and time_int < (network_adjusted_time + 60*60*2))
        else: 
            #UPDATE so that it is pulling the last 11 from memory if they aren't in DB yet
            is_valid = (time_int > average_time_last_11 )
    
    return is_valid

    
def validateBitcoinBlock(block_height, prior_block_bitcoin_height, realtime_validation=True):
    
    if getBlockCount() == 0:
        #prior_bitcoin_block_height = getCurrentBitcoinBlockHeight() - 6
        is_valid = True
        return is_valid
    
    else:
        #prior_bitcoin_block_height = queryGetPrevBitcoinBlock()
        prior_block_bitcoin_height_int = int.from_bytes(prior_block_bitcoin_height, byteorder='big')
        block_height_int = int.from_bytes(block_height, byteorder='big')
        
        #UPDATE should we have margin of a few bitcoin blocks? don't think so
        if realtime_validation==True:
            calculated_block_height = getCurrentBitcoinBlockHeight()
            is_valid = abs(calculated_block_height - block_height_int) <= bitcoin_block_range and block_height_int >= prior_block_bitcoin_height_int
        else:
            is_valid = block_height_int >= prior_block_bitcoin_height_int
        
    return is_valid    
    
    
def validateBits(bits):
    
    calculated_bits_bytes = get_bits_current_block()
    is_valid = calculated_bits_bytes == bits
        
    return is_valid
        
    
def validateBitcoinAddress(address):

    address = unhexlify(address)

    base58Decoder = base58.b58decode(address).hex()
    prefixAndHash = base58Decoder[:len(base58Decoder)-8]
    checksum = base58Decoder[len(base58Decoder)-8:]
    
    hash = prefixAndHash
    for x in range(1,3):
        hash = sha256(unhexlify(hash)).hexdigest()
    
    is_valid = checksum == hash[:8]

    return is_valid


def validateHeaderHash(
        version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce
        ):
    
    header_hash = calculateHeaderHash(
        version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce)
    
    block_target = get_target_from_bits(bits)

    is_valid = header_hash < block_target
    
    return is_valid


def getHeaders(start_hash,end_hash):
    
    print('get headers')
    print(start_hash,end_hash)
    
    if start_hash == unhexlify('0000000000000000000000000000000000000000000000000000000000000000'.encode('utf-8')):
        start_block = 1
    
    else:
        start_block = getBlockInformation(block_header = 'start_header')
        
    if end_hash == unhexlify('0000000000000000000000000000000000000000000000000000000000000000'.encode('utf-8')):
        end_block = start_block + max_headers_send
    
    else:
        end_block = getBlockInformation(block_header = 'end_header')
    
    end_block = min(end_block, start_block + max_headers_send, getMaxBlock())
        
    data = []
    print(start_block,end_block)
    
    for i in range(start_block, end_block):
        b = getBlockInformation(block_id = i)
        serialized_header = serialize_block_header_utf8(
            b.version,
            b.prev_block,     
            b.mrkl_root,
            b.time,
            b.bits,
            b.bitcoin_block_height,
            b.miner_bitcoin_address,
            b.nonce
        )
        
        data.append(serialized_header)
    
    print(data)
    
    return data


if __name__ == '__main__':
    
    print(getHeaders(unhexlify('0000000000000000000000000000000000000000000000000000000000000000'.encode('utf-8')),unhexlify('0000000000000000000000000000000000000000000000000000000000000000'.encode('utf-8'))))
    
    '''
    version = 1 
    prev_block = '0000000000000000000000000000000000000000000000000000000000000000'
    mrkl_root = '2b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4'
    time_ = 1614041015
    bits = 0x1d00ffff 
    nonce = 0x1f1471ce
    bitcoin_height = 680000
    miner_bitcoin_address = '31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668'
        
    version_bytes = version.to_bytes(2, byteorder = 'big')
    prev_block_bytes = unhexlify(prev_block)
    mrkl_root_bytes = unhexlify(mrkl_root)
    time_bytes = time_.to_bytes(5, byteorder = 'big')
    bits_bytes = bits.to_bytes(4, byteorder = 'big')
    bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
    miner_bitcoin_address_bytes = unhexlify(miner_bitcoin_address)
    nonce_bytes = nonce.to_bytes(4, byteorder = 'big')    
    
    transaction_1 = '00010001013b504f4c59474f4e20282839302039302c2039302038392e37343637342c203138302038392e37343637342c203138302039302c20393020393029292231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680000'
    transaction_2 = '00010001013b504f4c59474f4e20282839302039302c2039302038392e37343637342c203138302038392e37343637342c203138302039302c20393020393029292231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680000'
    transaction_3 = '00010001013b504f4c59474f4e20282839302039302c2039302038392e37343637342c203138302038392e37343637342c203138302039302c20393020393029292231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680000'
    
    transaction_1_bytes = unhexlify(transaction_1)
    transaction_2_bytes = unhexlify(transaction_2)
    transaction_3_bytes = unhexlify(transaction_3)
    transaction_set_bytes = [transaction_1_bytes,transaction_2_bytes,transaction_3_bytes]
    
    print('version: ' + str(validateVer(version_bytes)))
    print('prev block: ' + str(validatePrevBlock(prev_block_bytes)))
    print('mrkl: ' + str(validateMrklRoot(mrkl_root_bytes, transaction_set_bytes)))
    print('time: ' + str(validateTime(time_bytes)))
    print('bits: ' + str(validateBits(bits_bytes)))
    print('block: ' + str(validateBitcoinBlock(bitcoin_height_bytes)))
    print('bitcoin address: ' + str(validateBitcoinAddress(miner_bitcoin_address_bytes)))
    print('valid header: ' + str(validateHeaderHash(
        version_bytes,
        prev_block_bytes, 
        mrkl_root_bytes,
        time_bytes,
        bits_bytes,
        bitcoin_height_bytes,
        miner_bitcoin_address_bytes,
        nonce_bytes
        ))
    )    
    '''
    
    
