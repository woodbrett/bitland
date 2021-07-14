'''
Created on Dec 23, 2020

@author: brett_wood
'''
from node.blockchain.validate_block import validateBlockHeader, validateTransactions
from binascii import unhexlify, hexlify
from mining.mining import findValidHeader
from datetime import datetime
from node.blockchain.header_operations import *
from mining.create_landbase_transaction import *
from utilities.hashing import calculateMerkleRoot
from node.blockchain.block_serialization import *
from node.blockchain.block_operations import addBlock


def mineForLand():
    
    transaction_1_bytes = getLandbaseTransaction()
    #print(hexlify(transaction_1_bytes).decode('utf-8'))
    #transaction_2 = '000201010bc06709774a5c7a5dd292c451ededbee378340df618351f4abbdf077cd3d18f00401247cfe2a12d96481d8136d82264b9d127aaffcdd0fa611acfcaa1cc820ea83e661a4735328c91a53e90407b737a76693a9a257eeb0b7d876a564f1aabfe633d020101002c504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c302039302929409a19a65bc5b1fe8c3c4a60d5b2dbcbde27af0505b62a5ed46b3dc73e777202e8dbd6226eca1bb60bafdea37efc09a6faddf95bf22f699628b539948ddc372a8b02010030504f4c59474f4e28282d39302038392e37343637342c2d39302039302c302039302c2d39302038392e37343637342929401e410b1ecfb51fea3cd62bdf82107e54dddaf93629163b0365aba0b69406a987ac1bc3f5fd1cf812e4bfca854cfc3ec068402b7ec8ee2c73a66b1dd63032ebb800000000271007d000000007a12001902a626331716571723335646c723266616d6870797738763939767972707834376d67707378726c67786378'
    #transaction_2_bytes = unhexlify(transaction_2.encode('utf-8'))
    #transactions = [transaction_1_bytes, transaction_2_bytes]
    transactions = [transaction_1_bytes]
    
    version = 1 
    time_ = int(round(datetime.utcnow().timestamp(),0))
    start_nonce = 0
    bitcoin_height = int(requests.get(block_height_url).text)
    miner_bitcoin_address = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
    
    version_bytes = version.to_bytes(2, byteorder = 'big')
    prev_block_bytes = getPrevBlock()
    mrkl_root_bytes = calculateMerkleRoot(transactions)
    time_bytes = time_.to_bytes(5, byteorder = 'big')
    bits_bytes = get_bits_current_block() 
    bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
    miner_bitcoin_address_bytes = hexlify(miner_bitcoin_address.encode('utf-8'))
    start_nonce_bytes = start_nonce.to_bytes(4, byteorder = 'big')    
    
    header = findValidHeader(
        version_bytes,
        prev_block_bytes, 
        mrkl_root_bytes,
        time_bytes,
        bits_bytes,
        bitcoin_height_bytes,
        miner_bitcoin_address_bytes,
        start_nonce_bytes
    )
    
    serialized_block = serialize_block(header, transactions)
    block_hex = hexlify(serialized_block).decode('utf-8')
    
    return block_hex


def validateBlock(block):
    
    valid_block = True
    
    validate_block = validateBlockHeader(block)
    print(validate_block)
    
    valid_block = validate_block[0]
    
    if (valid_block == True):
      valid_block = validateTransactions(block)
    
    return valid_block


def populateBlock(block):
    
    block_height = addBlock(block);
    
    return block_height
    

if __name__ == '__main__':

    block = mineForLand()
    print(block)

    #transaction_1_bytes = getLandbaseTransaction()
    #print(hexlify(transaction_1_bytes).decode('utf-8'))
    #transaction_2 = '000201383934373566613833396333303866326335326637633038383033373534343730396137303735653964653165376631366534373037376564383234643634350040bbb44c83cbf1ee5c2509f07ef4ec1bab3b067feaf91ea1da4c50a306402e3843f7ba1065f62743ec197570863a3f40103eef51fc8066814fb25805e5089199ce01015f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e34313829298035646636303634626631393031353563323432313362343134623561633462333338626631363065353066386662366564653264663066363338323161623364663536336463653234353530653165626436323336373632316535373138373137613165346361656532653031666261313633656337383139343434623666610000'
    
    
    #block = '00010000000da7ec8bb04a126e6b4b760a2515464cf5e4d02a3aba69502a8584244f213859c96c8d008f87e5938de31dd553fc93343c81b1236298a995d03c3da8cb00604fc6431d0ffff0000a4bcb33313335346537373535366237343561373433343662353734643463373134623335353134633732373834313464353136313730373936353436373834313639333636380b16f4bb0001000100010051504f4c59474f4e28282d32322e352038392e37343637342c2d32322e352038392e35313836382c2d34352038392e35313836382c2d34352038392e37343637342c2d32322e352038392e37343637342929408925247388aabaf1ae797068220f1bba72b499911ba2d63fdc06511a95f3d70d4d07b7e3ffb3c37bddf7934ccd8db8a72947f5c998f009444d10a0d1c777a64f0000000000000000000000000000000000'
    
    block_bytes = unhexlify(block.encode('utf-8'))
    
    valid_block = validateBlock(block_bytes)
    #valid_block = [True]
    print("block validity: " +str(valid_block))
    
    if (valid_block[0] is True):
        block_height = populateBlock(block_bytes)
        print("added block " + str(block_height))
    
    else:
        print("error adding block")
    


