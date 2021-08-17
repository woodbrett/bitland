'''
Created on Feb 16, 2021

@author: brett_wood
'''
import codecs
from binascii import unhexlify, hexlify
from utilities.serialization import deserialize_text, serialize_text
from hashlib import sha256
from node.blockchain.block_serialization import deserialize_block
from node.blockchain.header_serialization import deserialize_block_header,\
    serialize_block_header

def calculateHeaderHashFromBlock(block_hex=None,block_bytes=None):
    
    if block_bytes == None:
        block_bytes = unhexlify(block_hex)

    header_bytes = deserialize_block(block_bytes)[0]
    headerhash_bytes = calculateHeaderHash(
        header_bytes.get('version'),
        header_bytes.get('prev_block'),
        header_bytes.get('mrkl_root'),
        header_bytes.get('time'),
        header_bytes.get('bits'),
        header_bytes.get('bitcoin_hash'),
        header_bytes.get('bitcoin_height'),
        header_bytes.get('bitcoin_last_64_mrkl'),
        header_bytes.get('miner_bitcoin_address'),
        header_bytes.get('nonce')
        )

    headerhash_hex = hexlify(headerhash_bytes).decode("utf-8")
    
    return headerhash_bytes 


def calculateHeaderHash(
        version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_hash,
        bitcoin_height,
        bitcoin_last_64_hash_mrkl,
        miner_bitcoin_address,
        nonce
        ):

    header_byte = serialize_block_header(version, prev_block, mrkl_root, time_, bits, bitcoin_hash, bitcoin_height, bitcoin_last_64_hash_mrkl, miner_bitcoin_address, nonce)

    #header_byte = ( version + prev_block + mrkl_root + time_ + bits + bitcoin_height + miner_bitcoin_address + nonce) 
    headerhash_byte = sha256(sha256(header_byte).digest()).digest()
    headerhash_hex = hexlify(headerhash_byte).decode("utf-8")
    
    return headerhash_byte 


def calculateMerkleRoot(transactions):
    
    storeHash = transactions[:]
        
    if (len(storeHash) % 2 != 0) :
        storeHash.append(storeHash[-1])
        
#    for i in range(0, len(storeHash) ):
#        storeHash[i] = codecs.decode(storeHash[i], "hex")[::-1]

    while (len(storeHash)> 1) : 
        j = 0;
        for i in range(0, len(storeHash) - 1) : 
            
            added = storeHash[i+1]
            
            storeHash[j] = sha256(added).digest()

            # hash of the i th leaf and i + 1 th leaf are concatenated
            # to find the hash parent to the both
            i += 2
            j += 1
        lastDelete = i - j;
        del storeHash[-lastDelete:];
        # as we now have the hash to the upper level of the tree, we delete the extra space in the array.
        # in each iteration of this loop the size of the storeHash list is halved.
    
    merkle_root = sha256(storeHash[0]).digest()
    
    return merkle_root


def calculateTransactionHash(transaction):
    
    transaction_hash = sha256(sha256(transaction).digest()).digest()
    
    return transaction_hash 




    