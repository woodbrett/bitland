'''
Created on Feb 26, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
from blockchain.transaction_serialization import serialize_transaction,\
    deserialize_transaction
from wallet.key_generation import *
import ecdsa


def createSimpleTransactionTransfer(input_transaction_hash, input_vout, input_private_key, input_public_key, polygon, planet_id):
    
    private_key_encoded = ecdsa.SigningKey.from_string(unhexlify(input_private_key),curve=ecdsa.SECP256k1)
    public_key_encoded = ecdsa.VerifyingKey.from_string(unhexlify(input_public_key),curve=ecdsa.SECP256k1)
    
    public_key_check = private_key_encoded.verifying_key
    print(public_key_check)
    print(hexlify(public_key_check.to_string()).decode("utf-8"))
    
    #print(input_private_key)
    #print(public_key)
    
    polygon_bytes = polygon.encode('utf-8')
    
    signature = private_key_encoded.sign(polygon_bytes)
    
    print(input_public_key)
    print(hexlify(signature).decode('utf-8'))
    print(polygon_bytes.decode('utf-8'))
    
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

    input_public_key = '420ba701f7a3c31c919395f45f701d78180c334f6e6328c90510232098030826664e80278ec0315bf4cf9335681d311dfaab0a4fd50d4deb151ef45656fa2d6d'
    input_private_key = 'd41ade7bba34f46935cae8902920bab387a8ebc92bb7a5667ed97d87fd3f3854'
    polygon = 'POLYGON((0 90,0 89.74674,-90 89.74674,-90 90,0 90))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '36242eb7bb49e133a31a0df59c16d5281e435acf3b4530cb8522e4405aa0e84c'
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    print(hexlify(simple_transaction).decode('utf-8'))
    
    print(deserialize_transaction(simple_transaction))

    '''
    select *, st_astext((st_dump(st_split(geom, st_setsrid(st_makeline(st_makepoint(st_xmax(geom), st_ymax(geom)), st_makepoint(st_xmin(geom), st_ymin(geom))),4326)))).geom)
    from bitland.utxo
    '''
    
    