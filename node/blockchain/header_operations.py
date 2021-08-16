'''
Created on Dec 23, 2020

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
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
from node.information.blocks import (
    getBlockCount,
    getPrevBlock,
    getMaxBlock,
    getBlock,
    getMedianBlockTime11
    )

def validateVer(version):
    
    version_int = int.from_bytes(version, byteorder='big')
    is_valid = version_int == 1
    
    return is_valid
    
def validatePrevBlock(prev_block, prev_block_input):

    if getBlockCount() == 0:
        prev_block_input = unhexlify('0000000000000000000000000000000000000000000000000000000000000000')
       
    is_valid = prev_block_input == prev_block
    return is_valid  


def getPrevBlockGuarded():
    
    if getBlockCount() == 0:
        node_prev_block = genesis_prev_block
    
    else:
        node_prev_block_hex = getPrevBlock()
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


#UPDATE
def validateBitcoinHash()    

    return True

    
def validateBitcoinBlock(block_height, prior_block_bitcoin_height, realtime_validation=True):
    
    
    if getBlockCount() == 0:
        prior_block_bitcoin_height_int = 0
    
    else:
        prior_block_bitcoin_height_int = int.from_bytes(prior_block_bitcoin_height, byteorder='big')
    
    block_height_int = int.from_bytes(block_height, byteorder='big')
    
    #UPDATE should we have margin of a few bitcoin blocks? don't think so
    if realtime_validation==True:
        calculated_block_height = getCurrentBitcoinBlockHeight()
        is_valid = abs(calculated_block_height - block_height_int) <= bitcoin_block_range and block_height_int >= prior_block_bitcoin_height_int
    else:
        is_valid = block_height_int >= prior_block_bitcoin_height_int
    
    return is_valid    


#UPDATE
def validateBitcoinLast64Mrkl()
    
    return True
    
    
def validateBits(bits):
    
    calculated_bits_bytes = get_bits_current_block()
    is_valid = calculated_bits_bytes == bits
        
    return is_valid
        
    
def validateBitcoinAddress(address):

    address_utf8 = address.decode('utf-8')
    is_valid = validateBitcoinAddressFromBitcoinNode(address_utf8)

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
        start_block = getBlock(block_header = 'start_header')
        
    if end_hash == unhexlify('0000000000000000000000000000000000000000000000000000000000000000'.encode('utf-8')):
        end_block = start_block + max_headers_send
    
    else:
        end_block = getBlock(block_header = 'end_header')
    
    end_block = min(end_block, start_block + max_headers_send, getMaxBlock())
        
    data = []
    print(start_block,end_block)
    
    for i in range(start_block, end_block):
        b = getBlock(block_id = i)
        serialized_header = serialize_block_header_utf8(
            b.get('version'),
            b.get('prev_block'),     
            b.get('mrkl_root'),
            b.get('time'),
            b.get('bits'),
            b.get('bitcoin_block_height'),
            b.get('miner_bitcoin_address'),
            b.get('nonce')
        )
        
        data.append(serialized_header)
    
    return data


if __name__ == '__main__':
    
    miner_address_bytes = b'bc1qccs269z2s4mftnu9r99chn537qwng235f28x99'
    
    x = validateBitcoinAddress(miner_address_bytes)
    print(x)
