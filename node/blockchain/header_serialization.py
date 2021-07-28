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
from datetime import datetime
from sys import byteorder

version_bytes_len = 2        
prev_block_bytes_len = 32
mrkl_root_bytes_len = 32
time_bytes_len = 5
bits_bytes_len = 4
bitcoin_height_bytes_len = 4
miner_bitcoin_address_bytes_len = 50
miner_bitcoin_address_len_bytes_len = 2
nonce_bytes_len = 4

#UPDATE need to think how to handle bitcoin miner addresses since they can be 34 or 42 characters hex, maybe just make it 21 bytes and end with 0s for ones that don't fill it up
def serialize_block_header_utf8(
        version,
        prev_block,     
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce
        ):
    
    version_bytes = version.to_bytes(version_bytes_len, byteorder = 'big')
    prev_block_bytes = unhexlify(prev_block)
    mrkl_root_bytes = unhexlify(mrkl_root)
    time_bytes = time_.to_bytes(time_bytes_len, byteorder = 'big')
    bits_bytes = bits.to_bytes(bits_bytes_len, byteorder = 'big')
    bitcoin_height_bytes = bitcoin_height.to_bytes(bitcoin_height_bytes_len, byteorder = 'big')
    miner_bitcoin_address_bytes = unhexlify(miner_bitcoin_address) 
    nonce_bytes = nonce.to_bytes(nonce_bytes_len, byteorder = 'big')
    
    header = serialize_block_header(
        version_bytes,
        prev_block_bytes,     
        mrkl_root_bytes,
        time_bytes ,
        bits_bytes ,
        bitcoin_height_bytes,
        miner_bitcoin_address_bytes,
        nonce_bytes
        )

    return header


def serialize_block_header(
        version_bytes,
        prev_block_bytes,     
        mrkl_root_bytes,
        time_bytes ,
        bits_bytes ,
        bitcoin_height_bytes,
        miner_bitcoin_address_bytes,
        nonce_bytes
        ):
    
    miner_bitcoin_address_combined_bytes = serializeMinerAddress(miner_bitcoin_address_bytes)
    
    header = (version_bytes + prev_block_bytes + mrkl_root_bytes + time_bytes + bits_bytes + bitcoin_height_bytes + miner_bitcoin_address_combined_bytes + nonce_bytes )

    return header


def serializeMinerAddress(miner_bitcoin_address_bytes):
    
    miner_bitcoin_address_len_bytes = len(miner_bitcoin_address_bytes).to_bytes(miner_bitcoin_address_len_bytes_len, byteorder='big')
    miner_bitcoin_address_combined_bytes = miner_bitcoin_address_len_bytes + miner_bitcoin_address_bytes
    miner_bitcoin_address_combined_hex = hexlify(miner_bitcoin_address_combined_bytes)
    
    for i in range(0,miner_bitcoin_address_bytes_len*2-len(miner_bitcoin_address_combined_hex)):
        miner_bitcoin_address_combined_hex =  miner_bitcoin_address_combined_hex + b'0'
    
    miner_bitcoin_address_combined_bytes = unhexlify(miner_bitcoin_address_combined_hex)
    
    return miner_bitcoin_address_combined_bytes


def deserialize_block_header(header, start_pos=0):
    
    counter = start_pos
    
    version = header[counter:(counter + version_bytes_len)]
    counter = counter + version_bytes_len
            
    prev_block = header[counter:(counter + prev_block_bytes_len)]
    counter = counter + prev_block_bytes_len
            
    mrkl_root = header[counter:(counter + mrkl_root_bytes_len)]
    counter = counter + mrkl_root_bytes_len
    
    time_ = header[counter:(counter + time_bytes_len)]
    counter = counter + time_bytes_len
    
    bits = header[counter:(counter + bits_bytes_len)]
    counter = counter + bits_bytes_len
    
    bitcoin_height = header[counter:(counter + bitcoin_height_bytes_len)]
    counter = counter + bitcoin_height_bytes_len
    
    miner_bitcoin_address_full = header[counter:(counter + miner_bitcoin_address_bytes_len)]
    counter = counter + miner_bitcoin_address_bytes_len
    
    miner_bitcoin_address_len = miner_bitcoin_address_full[0:miner_bitcoin_address_len_bytes_len]
    miner_bitcoin_address_len_int = int.from_bytes(miner_bitcoin_address_len,'big')
    miner_bitcoin_address = miner_bitcoin_address_full[miner_bitcoin_address_len_bytes_len:(miner_bitcoin_address_len_bytes_len+miner_bitcoin_address_len_int)]
    
    nonce = header[counter:(counter + nonce_bytes_len)]
    counter = counter + nonce_bytes_len
    counter_bytes = counter.to_bytes(4, byteorder = 'big')
    
    #change this to dict i think, lots of downstream calls on it though
    return(        
        version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce,
        counter_bytes
    )
    
