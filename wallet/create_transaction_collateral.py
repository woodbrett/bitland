'''
Created on Feb 26, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
from blockchain.transaction_serialization import serialize_transaction,\
    deserialize_transaction
from wallet.key_generation import *
import ecdsa


def createSimpleTransactionCollateral(input_transaction_hash, input_vout, input_private_key, input_public_key, input_polygon, polygon1, collateral_polygon, planet_id):
    
    private_key_encoded = ecdsa.SigningKey.from_string(unhexlify(input_private_key),curve=ecdsa.SECP256k1)
    public_key_encoded = ecdsa.VerifyingKey.from_string(unhexlify(input_public_key),curve=ecdsa.SECP256k1)
    
    input_polygon_bytes = input_polygon.encode('utf-8')
    polygon1_bytes = polygon1.encode('utf-8')
    polygon2_bytes = collateral_polygon.encode('utf-8')
    
    signature = private_key_encoded.sign(input_polygon_bytes)
    
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
    output_keys1 = generateRandomKeys()
    output_private_key1 = output_keys1[0]
    output_public_key1 = output_keys1[1]
    savePublicPrivateKeysDb(output_private_key1, output_public_key1)
    type = 1
    planet_id = planet_id
    coordinates = polygon1
    public_key = output_public_key1
    output_1 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    #output 2 - standard
    output_keys2 = generateRandomKeys()
    output_private_key2 = output_keys2[0]
    output_public_key2 = output_keys2[1]
    savePublicPrivateKeysDb(output_private_key2, output_public_key2)
    type = 2
    planet_id = planet_id
    coordinates = collateral_polygon
    public_key = output_public_key2
    output_2 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    outputs = [output_1, output_2]

    #contingencies
    miner_fee_sats = 10000
    miner_fee_blocks = 2000 #12960 max
    transfer_fee_sats = 500000
    transfer_fee_blocks = 400 #12960 max
    transfer_fee_address = 'bc1qeqr35dlr2famhpyw8v99vyrpx47mgpsxrlgxcx'
    contingencies = [miner_fee_sats.to_bytes(6, byteorder = 'big'),
                     miner_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_sats.to_bytes(6, byteorder = 'big'),
                     transfer_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_address.encode('utf-8')
                     ]

    serialized_transaction = serialize_transaction(transaction_version, inputs, outputs, contingencies)
    
    return serialized_transaction
    

if __name__ == '__main__':

    input_public_key = '32b3cdcca84d00e10d97eabdca2aaf466d47e5133e452fd5dd67a1f0d2e75a58b21c187c06f7b5da2074553c28fc24b749f3b6eeaea6d7f41a3d8dce7c5627df'
    input_private_key = '18220ca8b4aca63e218a66624003b662b8d9aae227f0b5c4488088c6d934c75d'
    input_polygon = 'POLYGON((0 90,0 89.74674,-90 89.74674,-90 90,0 90))'
    output_polygon1 = 'POLYGON((0 90,0 89.74674,-90 89.74674,0 90))'
    collateral_polygon = 'POLYGON((-90 89.74674,-90 90,0 90,-90 89.74674))'
    planet_id = 1
    vout = 0
    input_transaction_hash = 'b0bcaa0b93e0802533596449a9efa39f7137895c51baba2fa3eefe38cab8fff6'
    
    simple_transaction = createSimpleTransactionCollateral(input_transaction_hash, vout, input_private_key, input_public_key, input_polygon, output_polygon1, collateral_polygon, planet_id)
    print(hexlify(simple_transaction).decode('utf-8'))
    
    print(deserialize_transaction(simple_transaction))

    '''
    select *, st_astext((st_dump(st_split(geom, st_setsrid(st_makeline(st_makepoint(st_xmax(geom), st_ymax(geom)), st_makepoint(st_xmin(geom), st_ymin(geom))),4326)))).geom)
    from bitland.utxo
    '''
    
    