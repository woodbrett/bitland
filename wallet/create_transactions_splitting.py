'''
Created on Feb 26, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
from blockchain.transaction_serialization import serialize_transaction,\
    deserialize_transaction
from wallet.key_generation import *
import ecdsa


def createSimpleTransactionSplitting(input_transaction_hash, input_vout, input_private_key, input_public_key, input_polygon, polygon1, polygon2, planet_id):
    
    private_key_encoded = ecdsa.SigningKey.from_string(unhexlify(input_private_key),curve=ecdsa.SECP256k1)
    public_key_encoded = ecdsa.VerifyingKey.from_string(unhexlify(input_public_key),curve=ecdsa.SECP256k1)
    
    input_polygon_bytes = input_polygon.encode('utf-8')
    polygon1_bytes = polygon1.encode('utf-8')
    polygon2_bytes = polygon2.encode('utf-8')
    
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
    public_key = output_public_key
    output_1 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    #output 2 - standard
    output_keys2 = generateRandomKeys()
    output_private_key2 = output_keys2[0]
    output_public_key2 = output_keys2[1]
    savePublicPrivateKeysDb(output_private_key2, output_public_key2)
    type = 1
    planet_id = planet_id
    coordinates = polygon2
    public_key = output_public_key
    output_2 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    outputs = [output_1, output_2]

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

    input_public_key = 'a46a9598e469e7d938ae682593d7431b15f854e0545d250b8eb07eb4a7802e9fa194d48e7152ad0ed4d55f503240347b04caf7f08a95d87fb0a10b1e646f87cc'
    input_private_key = 'd8fc9e61ed6b575894ebe3048a699584d513693737ff9cb950bfb5c501cd646e'
    input_polygon = 'POLYGON((-22.5 89.74674,-22.5 89.51868,-45 89.51868,-45 89.74674,-22.5 89.74674))'
    output_polygon1 = 'POLYGON((-22.5 89.74674,-22.5 89.51868,-45 89.51868,-22.5 89.74674))'
    output_polygon2 = 'POLYGON((-45 89.51868,-45 89.74674,-22.5 89.74674,-45 89.51868))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '6477b8ded449793b26d9efcb8eafd0bead822eb26171d89a75458db0f2323455'
    
    simple_transaction = createSimpleTransactionSplitting(input_transaction_hash, vout, input_private_key, input_public_key, input_polygon, output_polygon1, output_polygon2, planet_id)
    print(hexlify(simple_transaction).decode('utf-8'))
    
    print(deserialize_transaction(simple_transaction))

    '''
    select *, st_astext((st_dump(st_split(geom, st_setsrid(st_makeline(st_makepoint(st_xmax(geom), st_ymax(geom)), st_makepoint(st_xmin(geom), st_ymin(geom))),4326)))).geom)
    from bitland.utxo
    '''
    
    