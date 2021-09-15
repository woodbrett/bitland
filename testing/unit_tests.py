'''
Created on Jul 25, 2021

@author: brett_wood
'''
from node.blockchain.transaction_serialization import deserializeTransaction
from binascii import hexlify, unhexlify
from node.blockchain.header_serialization import (
    serializeBlockHeaderUtf8,
    deserializeBlockHeader
    )
from _datetime import datetime
from utilities.bitcoin.bitcoin_requests import validateBitcoinAddressFromBitcoinNode
from utilities.gis_functions import (
    queryPolygonRules
    )
from node.networking.peering_functions import updatePeer


######### TRANSACTION TESTS #########

#validate that geometries with less than or equal to 6 decimal places are accepted
def validate_sub_six_digits_passes ():
    
    transaction_hex = '00020102677d5fc4a0b96d8978fbc50b60ea1b36f53906e26bd83384a2bcd38354f41e4e0240decdae58adf8fce02f2cf2f8073db49ee2a7b2ef056f5013f1e33cf047ef30fb47a7d2ce76547f70129ac12dc606bb67ffc1cb6a1d6bf58665a42a9030d064900101010070504f4c59474f4e28282d38392e3239363837352037362e3437383534392c2d38392e3239363837352037362e35343834322c2d38392e31343932342037362e35343834322c2d38392e3135363232372037362e3437383534392c2d38392e3239363837352037362e343738353439292940d0394277127fede9f032d2f4b2454c875b341b6fb87fff81f6e4f45ed7a50c4d5e635c221a2713bcea9a8bde513ccfebbfdab55e8ce74d182365e82c5991d9a20000000000000000000000000000000000'
    transaction_bytes = unhexlify(transaction_hex)
    outputs = deserializeTransaction(transaction_bytes)[2]
    status = queryPolygonRules(outputs)
    return status == True

#validate that geometries with more than 6 decimal places are rejected
def validate_more_six_digits_fails ():
    
    transaction_hex = '000201013c75b4c2a69b3a86e13ac62705a6cf2d8a56d7d8b8d18bf846c621d62478fe060040b9d9547ca43709613957fb96e64dd8e602aa9dd6188e49f116f3c9438a478eaec54b9d6a05a72bccf5b154434ad0f58203cdc9acbfbee4839f1f1f44a66e85d0010101005a504f4c59474f4e28282d33392e3337352038372e373637312c2d33392e3337352038372e36323530383332333132332c2d34352038372e36323530382c2d34352038372e373637312c2d33392e3337352038372e37363731292940bc1c01eccd6bb7c27891d1e44810393e533d770f9fdc4b2e00cd84d6505d7356fd85253f59367742d6a72674c28e07f3b47868677053e1160e0c699933d297250000000000000000000000000000000000'
    transaction_bytes = unhexlify(transaction_hex)
    outputs = deserializeTransaction(transaction_bytes)[2]
    status = queryPolygonRules(outputs)
    return status == False


######### SERIALIZATION TESTS #########

def validate_header_serialized_deserialized():

    prev_block = '0000000bd2a66af822f5cbc3a38a683afc3c9f9db74206f9c4ced40d8e55ce2c'
    mrkl_root = '2b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4'
    time_ = int(round(datetime.utcnow().timestamp(),0))
    bits = 0x1d00ffff 
    nonce = 0x1f1471ce
    bitcoin_hash = '2b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4'
    bitcoin_height = 680000
    bitcoin_last_64_mrkl = '2b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4'
    
    miner_bitcoin_address = '626331716363733236397a3273346d66746e753972393963686e35333771776e67323335663238783939'
    version = 1
    
    #test header serialization
    header = serializeBlockHeaderUtf8 (
        version,
        prev_block,     
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_hash,
        bitcoin_height,
        bitcoin_last_64_mrkl,
        miner_bitcoin_address,
        nonce
        )
    
    #print(header)

    #test header deserialization 
    deserialize_block_header_test = deserializeBlockHeader (header)
    
    if (deserialize_block_header_test.get('version') == version.to_bytes(2, byteorder = 'big')
        and deserialize_block_header_test.get('prev_block') == unhexlify(prev_block)
        and deserialize_block_header_test.get('mrkl_root') == unhexlify(mrkl_root)
        and deserialize_block_header_test.get('time') == time_.to_bytes(5, byteorder = 'big')
        and deserialize_block_header_test.get('bits') == bits.to_bytes(4, byteorder = 'big')
        and deserialize_block_header_test.get('bitcoin_hash') == unhexlify(bitcoin_hash)
        and deserialize_block_header_test.get('bitcoin_height') == bitcoin_height.to_bytes(4, byteorder = 'big')
        and deserialize_block_header_test.get('bitcoin_last_64_mrkl') == unhexlify(bitcoin_last_64_mrkl)
        and deserialize_block_header_test.get('miner_bitcoin_address') == unhexlify(miner_bitcoin_address)
        and deserialize_block_header_test.get('nonce') == nonce.to_bytes(4, byteorder = 'big')
        ):
        return True
    
    else: 
        return False


######### VALIDATION TESTS #########

def validate_bitcoin_addresses():
    
    if validateBitcoinAddressFromBitcoinNode('bc1qamgmd4s53pq5y0ejlnps580yujpvyhvanvxc2y') == False:
        return False
    if validateBitcoinAddressFromBitcoinNode('bc1qamgmd4s53pq5y0ejlnaps580yujpvyhvanvx2y') == True:
        return False

    return True


######### PEER TESTS #########

def validate_peer_functions():
    
    if updatePeer('1.2.3.4', port=8111, status='connected',derive_peer_auth_key=True) != 0:
        return False
    
    return True


if __name__ == '__main__':
    
    ######### TRANSACTION TESTS #########
    print(validate_sub_six_digits_passes())
    print(validate_more_six_digits_fails())
    
    ######### SERIALIZATION TESTS #########
    print(validate_header_serialized_deserialized())
    
    ######### VALIDATION TESTS #########
    print(validate_bitcoin_addresses())
    
    ######### PEER TESTS #########
    print(validate_peer_functions())
    
    
    
    