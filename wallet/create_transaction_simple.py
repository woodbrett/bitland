'''
Created on Feb 26, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
from node.blockchain.transaction_serialization import (
    serialize_transaction,
    deserialize_transaction
)
from wallet.key_generation import *
import ecdsa

def createSimpleTransactionTransfer(input_transaction_hash, input_vout, input_private_key, input_public_key, polygon, planet_id):
    
    private_key_encoded = ecdsa.SigningKey.from_string(unhexlify(input_private_key),curve=ecdsa.SECP256k1)
    public_key_encoded = ecdsa.VerifyingKey.from_string(unhexlify(input_public_key),curve=ecdsa.SECP256k1)
    
    public_key_check = private_key_encoded.verifying_key
    #print(public_key_check)
    #print(hexlify(public_key_check.to_string()).decode("utf-8"))
    
    #print(input_private_key)
    #print(public_key)
    
    polygon = polygon.replace(", ","," ) # remove all spaces
    polygon = polygon.replace(" (","(" ) # remove all spaces
    polygon_bytes = polygon.encode('utf-8')
    
    signature = private_key_encoded.sign(polygon_bytes)
    
    
    print(public_key_encoded)
    print(polygon_bytes)
    #signature = b'\x03z^8\xe70\x07&\x18(\xfbO\xc34zR\x02#\x96\xb4.s\x1e#\x99-\x97\x7f\x00T\x03H&~\x86\xcf\x19s\xf9)\xa3\xa8i\xe5\xa0\x16`\xb8\x80\x81.\xb1z\xcaHO\xa4\x05h\x9c\x18x\xcc\x01'
    print(signature)
    
    print(public_key_encoded.verify(signature, polygon_bytes))

    #print((input_transaction_hash).encode('utf-8'))
    #print(unhexlify(input_transaction_hash))
    
    output_keys = generateRandomKeys()
    output_private_key = output_keys[0]
    output_public_key = output_keys[1]

    savePublicPrivateKeysDb(output_private_key, output_public_key)
    
    transaction_version = 2
    transaction_version = transaction_version.to_bytes(2, byteorder = 'big')
        
    #input 1 - standard
    type = 1 #standard
    transaction_hash = input_transaction_hash
    vout = input_vout
    signature = signature
    input_1 = [type.to_bytes(1, byteorder = 'big'), unhexlify(transaction_hash), vout.to_bytes(1, byteorder = 'big'), signature]

    inputs = [input_1]
    
    #output 1 - standard
    type = 1
    planet_id = planet_id
    coordinates = polygon
    public_key = output_public_key
    output_1 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    outputs = [output_1]

    #contingencies
    miner_fee_sats = 0
    miner_fee_blocks = 0 #12960 max
    transfer_fee_sats = 0
    transfer_fee_blocks = 0 #12960 max
    transfer_fee_address = ''
    contingencies = [miner_fee_sats.to_bytes(6, byteorder = 'big'),
                     miner_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_sats.to_bytes(6, byteorder = 'big'),
                     transfer_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_address.encode('utf-8')
                     ]

    serialized_transaction = serialize_transaction(transaction_version, inputs, outputs, contingencies)
    
    return serialized_transaction
    

if __name__ == '__main__':

    input_public_key = '2f499fc81d1fac1018ecc5e35d971f5e38c9507de0a3faa78da21cd5f22deb130ea38f96bbccc791c1b91765442a157a92142f8cd5ccf135bbcb7a20d05f5322'
    input_private_key = '403c06b0f058d7f242aca5901ecb951ae4d41a9c02ff2ca96ca29c71c130f29c'
    polygon = 'POLYGON((-39.375 87.7671, -39.375 87.62508, -45 87.62508, -45 87.7671, -39.375 87.7671))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '3c75b4c2a69b3a86e13ac62705a6cf2d8a56d7d8b8d18bf846c621d62478fe06'
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    print(hexlify(simple_transaction).decode('utf-8'))
    
    print(deserialize_transaction(simple_transaction))
    
    

    
    