'''
Created on Feb 22, 2021

@author: brett_wood
'''
from blockchain.transaction_serialization import *
from blockchain.header_serialization import *
from blockchain.block_serialization import *
from utilities.hashing import *
from datetime import datetime

'''
# TRANSACTION1 calculations
version = 1
inputs = []
output_1_planet = 1
output_1_shape = 'POLYGON ((90 90, 90 89.74674, 180 89.74674, 180 90, 90 90))'
output_1_script = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
contingencies = []
claims = []

version_bytes = version.to_bytes(2, byteorder = 'big')
inputs_bytes = inputs
output_1_planet_bytes = output_1_planet.to_bytes(1, byteorder = 'big')
output_1_shape_bytes = output_1_shape.encode('utf-8')

output_1_script_bytes = output_1_script.encode('utf-8')
output_1_bytes = [output_1_planet_bytes,output_1_shape_bytes,output_1_script_bytes]
outputs_bytes = [output_1_bytes]
contingencies_bytes = contingencies
claims_bytes = claims

serialized_transaction_1 = serialize_transaction(
    version_bytes, #version
    inputs_bytes, #inputs
    outputs_bytes, #outputs
    contingencies_bytes, #contingencies
    claims_bytes #claims
    )

# TRANSACTION2 calculations
version = 1
inputs = []
output_1_planet = 1
output_1_shape = 'POLYGON ((90 90, 90 89.74674, 180 87.74674, 180 90, 90 89))'
output_1_script = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
contingencies = []
claims = []

version_bytes = version.to_bytes(2, byteorder = 'big')
inputs_bytes = inputs
output_1_planet_bytes = output_1_planet.to_bytes(1, byteorder = 'big')
output_1_shape_bytes = output_1_shape.encode('utf-8')
output_1_script_bytes = output_1_script.encode('utf-8')
output_1_bytes = [output_1_planet_bytes,output_1_shape_bytes,output_1_script_bytes]
outputs_bytes = [output_1_bytes]
contingencies_bytes = contingencies
claims_bytes = claims

serialized_transaction_2 = serialize_transaction(
    version_bytes, #version
    inputs_bytes, #inputs
    outputs_bytes, #outputs
    contingencies_bytes, #contingencies
    claims_bytes #claims
    )

serialized_transaction_3 = serialized_transaction_1

print(serialized_transaction_1)


serialized_transactions = []
serialized_transactions.append(serialized_transaction_1)
serialized_transactions.append(serialized_transaction_2)
serialized_transactions.append(serialized_transaction_3)
print(serialized_transactions)
'''

#merkle_root = calculateMerkleRoot(serialized_transactions)
#print(merkle_root)
#print(hexlify(merkle_root).decode('utf-8'))


#0000000466ba091880d57e53a64345e1c0b84db215918b4cc6b171c6eeba8114
#105714608

print(hex(105714608))

transaction_1 = '000100010133504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c30203930292940ea032a860b9b4cc136ca208e14865839bb300a76237d816f45c587ae37a01355577aebbb4f810ba062ef1352b25feb62257d86f59f967e4c8587c867a3756afa0000'
transaction_1_bytes = unhexlify(transaction_1)
transaction_set_bytes = [transaction_1_bytes]
serialized_transactions = [transaction_1_bytes]

merkle_root = calculateMerkleRoot(transaction_set_bytes) 
print(merkle_root)   
print(hexlify(merkle_root))  
print(hexlify(merkle_root).decode('utf-8'))

# HEADER calculations
version = 1 
prev_block = '0000000000000000000000000000000000000000000000000000000000000000'
#mrkl_root = '2b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4'
time_ = int(round(datetime.utcnow().timestamp(),0))
bits = 0x1d0ffff0 
nonce = 105714608
bitcoin_height = 671782
miner_bitcoin_address = '31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668'
    
version_bytes = version.to_bytes(2, byteorder = 'big')
prev_block_bytes = unhexlify(prev_block)
mrkl_root_bytes = merkle_root
time_bytes = time_.to_bytes(5, byteorder = 'big')
bits_bytes = bits.to_bytes(4, byteorder = 'big')
bitcoin_height_bytes = bitcoin_height.to_bytes(4, byteorder = 'big')
miner_bitcoin_address_bytes = unhexlify(miner_bitcoin_address)
nonce_bytes = nonce.to_bytes(4, byteorder = 'big')    

serialized_header = serialize_block_header(
    version_bytes,
    prev_block_bytes, 
    mrkl_root_bytes,
    time_bytes,
    bits_bytes,
    bitcoin_height_bytes,
    miner_bitcoin_address_bytes,
    nonce_bytes
    )

print(serialized_header)

header = '000100000000000000000000000000000000000000000000000000000000000000001e01968781e0c779415ac074f2ad3777a1091fbd495bd99f7cfaf1aab83219080060357e371d0ffff0000a406231354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680c12a77e'
serialized_header = unhexlify(header)
print(serialized_header)

#BLOCK

serialized_block = serialize_block(serialized_header, serialized_transactions)
print(serialized_block)
print(hexlify(serialized_block).decode('utf-8'))

#e13c9c38f91688f9d3b35a793f1e4e28d7e160694d014f3ac4ca4f4dfa5ce164
#b'\xce\x00\x01\x00\x01\x01;POLYGON ((90 90, 90 89.74'
