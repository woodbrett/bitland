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
    headerhash_bytes = calculateHeaderHash(header_bytes[0],header_bytes[1],header_bytes[2],header_bytes[3],header_bytes[4],header_bytes[5],header_bytes[6],header_bytes[7])
    headerhash_hex = hexlify(headerhash_bytes).decode("utf-8")
    
    return headerhash_bytes 


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

    header_byte = serialize_block_header(version, prev_block, mrkl_root, time_, bits, bitcoin_height, miner_bitcoin_address, nonce)

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

    transactions = [b'\x00\x02\x03\x01\xc9/\xfe\xd2\x1a\x11\xdbNX)\xce_\x02\x7f\xf0\x9af\x9a\xad\xc7\x81)\xa6\xe1\x8420\x8c\xdc\xa7~\xc7\x00@D|\x07\xfd^Pm:f\xe5\x93\'3\x01Ag\x0c\xfd0D\x85\xb9~\xf9\xee\xa8\xe4\x94*\xb7\xb0\xc2\xb0\x95\x00j\xa8a]Qv0\x08\xb2\r\x16\\\x8b\xd8\x96\xd1E\xe2\xb3\x9c\x1d\x06nEi\x05\xd5\xf9\xb4\x016\xb5\xf5\x86\x8e\xbbx\x95\xf4\x11\n;\x8a\x048\xd7U\xa0\xe2\xc7)\x98n\xf9\xce\x9f\x16r?K\xed\x81\x00@`{\xc6+\x87\x14\x89"\xf1Wj\x94\x8c\xcfo,\x89\x9e0\xf7\x02\xa5\xa8F\xaf\x17\x0c\xb5\xb7\xec\x1a\'W:,\xcf\xc3\xfd\xae\x1fJ1\x1e+o\xb3\xe0\xeb\xa4p\xd5Gn\x1a6O\x8e\xfaT\xa5B\xe8\xa8}\x01\\\xc1\x18\x1cU(\xc8\x8fMJ\x8e^\x9cV\xd48\x01\xe7\xf3c\xd9\xc2\xa3\x14\r\x9d\xbdY\xd4\xce\r=\x00@\xab&\x96\xf2\xec\x11\x00\xb1\xd8\xac\xfd$U\xf7A\xc0:\x8eM\x9c\xf92\xff\xac\xbefp\xf1|\xa9\xb2y\xcd\xe0\x18G\x1d\xe2Ee\xa6\xc2`\x9c?\xa7\xe36\r\x0b\xc6\x91\xb7\xb8\xfd\x11m\x14bI\x01\x9a\xb0\x14\x03\x01\x01\x00\xd1MULTIPOLYGON(((-94.21875 46.6632,-94.21875 46.52964,-94.409135 46.52964,-94.333189 46.6632,-94.21875 46.6632)),((-94.21875 46.2636,-94.21875 46.13094,-94.474127 46.13094,-94.422537 46.2636,-94.21875 46.2636)))@\xa5\xf0G\x96\xf6\x17\x17a$\x05y\xc7u~\x94\x93+dV\x17K:\x12w_:\x96\x9c\xd4\xd8&\xf1\xd6\xb5\x89\x143\xc4L\xd0\xfazqc\xa4un\xb7\xae\x900\xb2\xec\t\x81\xde\xc0\x01f\xcdi^\xaa\\\x01\x01\x00\xdbMULTIPOLYGON(((-94.474127 46.13094,-94.570313 46.13094,-94.570313 46.2636,-94.422537 46.2636,-94.474127 46.13094)),((-94.921875 47.33604,-94.921875 47.20086,-95.273438 47.20086,-95.273438 47.33604,-94.921875 47.33604)))@2\x97\x12cD\xdb\xc0a\xed1W\xe7\xec\xac\xe1K\xbd\xa9\x01^&\xad\x1aJ\t\xdb(u8\xc1\xdd\xcf\xb2esC\x97\x1e\x9c2\xf59\xc6\xb5A\xbeH\x10\xc2\xaf6@\xe2N!+\x88D\xe9\xa3\x94\xbbI\x04\x02\x01\x00lPOLYGON((-94.409135 46.52964,-94.570313 46.52964,-94.570313 46.6632,-94.333189 46.6632,-94.409135 46.52964))@\xc3\x909\xaa:\xff\xdfN\xc2\xb9cn,\xa0\xfdf\x07\xb7 &\xd6b\x98\x07\'\xf1\xc4\x1d\x84\x1buM\xe3&\x93C\xde\x80\\ 9/\x90\xdalh\x03\xe7$\xf9\x1f\xb9\x1bG\x15\xf3>L\xbb.\xd4\xc6N6\x00\x00\x00\x00\xc3P\x07\xd0\x00\x00\x00\x00\xc3P\x07\xd0T6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b7773', b'\x00\x01\x00\x01\x00\x01\x00sPOLYGON((-100.195313 51.86556,-100.195313 51.71742,-100.546875 51.71742,-100.546875 51.86556,-100.195313 51.86556))@\x8b1V\x0f\x1a,\x8b\xdatz\x9c2\x0b\xda;\x94X\x10X\xa2\xc8\x1f\xcc\x9d\xc8jsg\x1fm\xbd\xd3\x19]S%\xb0\xbdj\xf4\xf2\x1fpy\x0b\x95K\x954\xaa#\xa1\xbe\x01\xd1\xc5\x86\xe1l\x8d\xf3G\xb39\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']

    merkle_root = calculateMerkleRoot(transactions)    
    print(merkle_root)
    
    #b'\x8ck\x83\x1b\xb7\xb5\x02\x8d\x1c\x95.!\x12\x0e\xd7v\x82\xdf\x99h\x92P\x1d4x\xaago\xa8$S\xc5'

    