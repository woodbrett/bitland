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
     
    version_byte = version.to_bytes(2, byteorder = 'big')
    print(version)
    print(version_byte)
    prev_block_byte = unhexlify(prev_block)
    mrkl_root_byte = unhexlify(mrkl_root)
    time_byte = time_.to_bytes(5, byteorder = 'big')
    bits_byte = bits.to_bytes(4, byteorder = 'big')
    bitcoin_height_byte = bitcoin_height.to_bytes(4, byteorder = 'big')
    miner_bitcoin_address_byte = hexlify(miner_bitcoin_address.encode('utf-8'))
    print(miner_bitcoin_address)
    print(miner_bitcoin_address_byte)
    nonce_byte = nonce.to_bytes(4, byteorder = 'big')
    
    header = (version_byte + prev_block_byte + mrkl_root_byte + time_byte + bits_byte + bitcoin_height_byte + miner_bitcoin_address_byte + nonce_byte)
    #print(hexlify(header))
    #print(hexlify(header).decode('utf-8'))
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
     
    header = (version_bytes + prev_block_bytes + mrkl_root_bytes + time_bytes + bits_bytes + bitcoin_height_bytes + miner_bitcoin_address_bytes + nonce_bytes )
    #print(hexlify(header))
    #print(hexlify(header).decode('utf-8'))
    return header


def deserialize_block_header(header, start_pos=0):

    counter = start_pos
    version_bytes = 2        
    prev_block_bytes = 32
    mrkl_root_bytes = 32
    time_bytes = 5
    bits_bytes = 4
    bitcoin_height_bytes = 4
    miner_bitcoin_address_bytes = 68
    nonce_bytes = 4
    
    version = header[counter:(counter + version_bytes)]
    counter = counter + version_bytes
            
    prev_block = header[counter:(counter + prev_block_bytes)]
    counter = counter + prev_block_bytes
            
    mrkl_root = header[counter:(counter + mrkl_root_bytes)]
    counter = counter + mrkl_root_bytes
    
    time_ = header[counter:(counter + time_bytes)]
    counter = counter + time_bytes
    
    bits = header[counter:(counter + bits_bytes)]
    counter = counter + bits_bytes
    
    bitcoin_height = header[counter:(counter + bitcoin_height_bytes)]
    counter = counter + bitcoin_height_bytes
    
    miner_bitcoin_address = header[counter:(counter + miner_bitcoin_address_bytes)]
    counter = counter + miner_bitcoin_address_bytes
    
    nonce = header[counter:(counter + nonce_bytes)]
    counter = counter + nonce_bytes
    counter_bytes = counter.to_bytes(4, byteorder = 'big')
        
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
    

def deserialize_block_header_utf8(header_utf8):

    counter = 0
    version_bytes = 2        
    prev_block_bytes = 32
    mrkl_root_bytes = 32
    time_bytes = 5
    bits_bytes = 4
    nonce_bytes = 4
    bitcoin_height_bytes = 4
    miner_bitcoin_address_bytes = 34
    
    version = int.from_bytes(unhexlify(header)[counter:(counter + version_bytes)], byteorder='big')
    counter = counter + version_bytes
            
    prev_block = encode(unhexlify(header)[counter:(counter + prev_block_bytes)],'hex').decode('utf-8')
    counter = counter + prev_block_bytes
            
    mrkl_root = encode(unhexlify(header)[counter:(counter + mrkl_root_bytes)],'hex').decode('utf-8')
    counter = counter + mrkl_root_bytes
    
    time_ = int.from_bytes(unhexlify(header)[counter:(counter + time_bytes)], byteorder='big')
    counter = counter + time_bytes
    
    bits = int.from_bytes(unhexlify(header)[counter:(counter + bits_bytes)], byteorder='big')
    counter = counter + bits_bytes
    
    nonce = int.from_bytes(unhexlify(header)[counter:(counter + nonce_bytes)], byteorder='big')
    counter = counter + nonce_bytes
    
    bitcoin_height = int.from_bytes(unhexlify(header)[counter:(counter + bitcoin_height_bytes)], byteorder='big')
    counter = counter + bitcoin_height_bytes
    
    miner_bitcoin_address = deserialize_text(encode(unhexlify(header)[counter:(counter + miner_bitcoin_address_bytes)],'hex').decode('utf-8'))
    counter = counter + miner_bitcoin_address_bytes
        
    return(        
        version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce,
        counter
    )
    

if __name__ == '__main__':
    
    a = 0x1
    b = 0x2

    
    #prev_block = '0000000bd2a66af822f5cbc3a38a683afc3c9f9db74206f9c4ced40d8e55ce2c'
    prev_block = 0x0000000bd2a66af822f5cbc3a38a683afc3c9f9db74206f9c4ced40d8e55ce2c
    print(unhexlify(prev_block))
    mrkl_root = '2b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4'
    time_ = int(round(datetime.utcnow().timestamp(),0))
    bits = 0x1d00ffff 
    print(bits.to_bytes(4, byteorder = 'big'))
    nonce = 0x1f1471ce
    bitcoin_height = 680000
    miner_bitcoin_address = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
    
    print(hexlify(miner_bitcoin_address.encode('utf-8')))
    print(unhexlify(prev_block) + hexlify(miner_bitcoin_address.encode('utf-8')))

    #test header serialization
    header = serialize_block_header_utf8(
        version,
        prev_block,     
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce
        )
    
    print(header)
    print("valid header: " + unhexlify(header).decode('utf-8'))
    
    header = serialize_block_header(
        version.to_bytes(2, byteorder = 'big'),
        unhexlify(prev_block),
        unhexlify(mrkl_root),
        time_.to_bytes(5, byteorder = 'big'),
        bits.to_bytes(4, byteorder = 'big'),
        bitcoin_height.to_bytes(4, byteorder = 'big'),
        hexlify(miner_bitcoin_address.encode('utf-8')),
        nonce.to_bytes(4, byteorder = 'big')
    )
    
    print(header)
    print(len(header))
    print(hexlify(header))
    
    #test header deserialization 
    test_header = '000100000000000000000000000000000000000000000000000000000000000000006a0acd19b3c0dcf3af2f8f159b79a0391a473efcbc9d16588ed8381950c78958005faa01fd1710c4331f1471ce000a604031354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668' 
    print(test_header.encode('utf-8'))
    deserialized_header = deserialize_block_header(test_header.encode('utf-8'))
    print(deserialized_header)
        
    serialized_block_header_test = serialize_block_header(        
        version.to_bytes(2, byteorder = 'big'),
        unhexlify(prev_block),
        unhexlify(mrkl_root),
        time_.to_bytes(5, byteorder = 'big'),
        bits.to_bytes(4, byteorder = 'big'),
        bitcoin_height.to_bytes(4, byteorder = 'big'),
        unhexlify(miner_bitcoin_address),
        nonce.to_bytes(4, byteorder = 'big')
        )
    
    deserialize_block_header_test = deserialize_block_header(serialized_block_header_test)
    
    print(serialized_block_header_test)
    print(deserialize_block_header_test)
    
    print(deserialize_block_header_test[0] == version.to_bytes(2, byteorder = 'big'))
    print(deserialize_block_header_test[1] == unhexlify(prev_block))
    print(deserialize_block_header_test[2] == unhexlify(mrkl_root))
    print(deserialize_block_header_test[3] == time_.to_bytes(5, byteorder = 'big'))
    print(deserialize_block_header_test[4] == bits.to_bytes(4, byteorder = 'big'))
    print(deserialize_block_header_test[5] == bitcoin_height.to_bytes(4, byteorder = 'big'))
    print(deserialize_block_header_test[6] == unhexlify(miner_bitcoin_address))
    print(deserialize_block_header_test[7] == nonce.to_bytes(4, byteorder = 'big'))

