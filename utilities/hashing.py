'''
Created on Feb 16, 2021

@author: brett_wood
'''
import codecs
from binascii import unhexlify, hexlify
from utilities.serialization import deserialize_text, serialize_text
from hashlib import sha256

def calculateHeaderHash(
        version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce
        ):

    header_byte = ( version + prev_block + mrkl_root + time_ + bits + bitcoin_height + miner_bitcoin_address + nonce) 
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


if __name__ == '__main__':

    #test input and output match
    '''
    version = 1
    prev_block = '0000000000000000000000000000000000000000000000000000000000000000'
    mrkl_root = '6a0acd19b3c0dcf3af2f8f159b79a0391a473efcbc9d16588ed8381950c78958'
    time_ = 1604977149
    bits = 0x1710c433
    nonce = 0x1f1471ce
    bitcoin_height = 680000
    miner_bitcoin_address = '31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668'
    
    serialized_block_header_test = calculateHeaderHash(version ,
                                                          prev_block, 
                                                          mrkl_root ,
                                                          time_,
                                                          bits ,
                                                          bitcoin_height ,
                                                          miner_bitcoin_address ,
                                                          nonce 
                                                          )
    
    print(serialized_block_header_test)
    
    transaction_1 = '00010001013b504f4c59474f4e20282839302039302c2039302038392e37343637342c203138302038392e37343637342c203138302039302c20393020393029292231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680000'
    transaction_2 = '00010001013b504f4c59474f4e20282839302039302c2039302038392e37343637342c203138302038392e37343637342c203138302039302c20393020393029292231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680000'
    transaction_3 = '00010001013b504f4c59474f4e20282839302039302c2039302038392e37343637342c203138302038392e37343637342c203138302039302c20393020393029292231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680000'
    
    transaction_1_bytes = unhexlify(transaction_1)
    transaction_2_bytes = unhexlify(transaction_2)
    transaction_3_bytes = unhexlify(transaction_3)
    transaction_set_bytes = [transaction_1_bytes,transaction_2_bytes,transaction_3_bytes]

    test_merkle = calculateMerkleRoot(transaction_set_bytes)
    print(test_merkle)
    print(hexlify(test_merkle).decode('utf-8'))
    '''
    
    transaction_1 = '000100010133504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c30203930292940ea032a860b9b4cc136ca208e14865839bb300a76237d816f45c587ae37a01355577aebbb4f810ba062ef1352b25feb62257d86f59f967e4c8587c867a3756afa0000'
    transaction_1_bytes = unhexlify(transaction_1)
    transaction_set_bytes = [transaction_1_bytes]

    merkle_root = calculateMerkleRoot(transaction_set_bytes)    
    print(merkle_root)
    
    
    