'''
Created on Feb 26, 2021

@author: brett_wood
'''
from utilities.sql_utils import executeSql
from node.blockchain.transaction_serialization import (
    serializeTransaction,
    deserializeTransaction
)
from wallet.key_generation import *
import ecdsa
from node.information.utxo import getUtxo
import json

def createSimpleTransactionTransfer(input_transaction_hash, input_vout, input_private_key, input_public_key, polygon, planet_id, input_spend_type):
    
    private_key_encoded = ecdsa.SigningKey.from_string(unhexlify(input_private_key),curve=ecdsa.SECP256k1)
    public_key_encoded = ecdsa.VerifyingKey.from_string(unhexlify(input_public_key),curve=ecdsa.SECP256k1)
    
    public_key_check = private_key_encoded.verifying_key
    
    #logic to remove spaces that can happen from copying
    polygon = polygon.replace(", ","," ) # remove all spaces
    polygon = polygon.replace(" (","(" ) # remove all spaces
    polygon_bytes = polygon.encode('utf-8')
    
    signature = private_key_encoded.sign(polygon_bytes)
    
    output_keys = generateRandomKeys()
    output_private_key = output_keys[0]
    output_public_key = output_keys[1]

    savePublicPrivateKeysDb(output_private_key, output_public_key)
    
    transaction_version = 2
    transaction_version = transaction_version.to_bytes(2, byteorder = 'big')
        
    #input 1 - standard
    type = input_spend_type 
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

    serialized_transaction = serializeTransaction(transaction_version, inputs, outputs, contingencies)
    
    return serialized_transaction


def createTransaction1(transaction_version, inputs, outputs, contingencies):
    #inputs [input_version, input_transaction_hash, input_vout, input_private_key, input_public_key]
    #outputs [output_version, planet, shape, public_script (address)]
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    
    inputs_processed = []
    outputs_processed = []
    transaction_version = 2
    transaction_version = transaction_version.to_bytes(2, byteorder = 'big')
    
    for i in range(0,len(inputs)):  
        
        input_type = inputs[i][0]
        input_transaction_hash = inputs[i][1]
        input_vout = inputs[i][2]
        input_public_key = inputs[i][3]
        input_private_key = inputs[i][4]
        
        utxo = getUtxo(transaction_hash=input_transaction_hash, vout=input_vout)
        coordinates = getUtxo(transaction_hash=input_transaction_hash, vout=input_vout).get('shape')
        coordinates = coordinates.replace(", ","," ) # remove all spaces
        coordinates = coordinates.replace(" (","(" ) # remove all spaces
        
        private_key_encoded = ecdsa.SigningKey.from_string(unhexlify(input_private_key),curve=ecdsa.SECP256k1)
        public_key_encoded = ecdsa.VerifyingKey.from_string(unhexlify(input_public_key),curve=ecdsa.SECP256k1)
        
        public_key_check = private_key_encoded.verifying_key
        signature = private_key_encoded.sign(coordinates.encode('utf-8'))

        #input 1 - standard
        type = input_type
        transaction_hash = input_transaction_hash
        vout = input_vout
        signature = signature
        input = [type.to_bytes(1, byteorder = 'big'), unhexlify(transaction_hash), vout.to_bytes(1, byteorder = 'big'), signature]
        
        inputs_processed.append(input)

    
    for i in range(0,len(outputs)):
        
        output_version = outputs[i][0]
        planet_id = outputs[i][1]
        coordinates = outputs[i][2]
        address = outputs[i][3]
    
        #logic to remove spaces that can happen from copying
        coordinates = coordinates.replace(", ","," ) # remove all spaces
        coordinates = coordinates.replace(" (","(" ) # remove all spaces      
    
        if address == None:
            output_keys = generateRandomKeys()
            output_private_key = output_keys[0]
            address = output_keys[1]
    
            savePublicPrivateKeysDb(output_private_key, address)

        output = [output_version.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(address)]
    
        outputs_processed.append(output)
        
    
    #contingencies
    miner_fee_sats = contingencies[0]
    miner_fee_blocks = contingencies[1] #12960 max
    transfer_fee_sats = contingencies[2]
    transfer_fee_blocks = contingencies[3] #12960 max
    transfer_fee_address = contingencies[4]
    contingencies = [miner_fee_sats.to_bytes(6, byteorder = 'big'),
                     miner_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_sats.to_bytes(6, byteorder = 'big'),
                     transfer_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_address.encode('utf-8')
                     ]

    serialized_transaction = serializeTransaction(transaction_version, inputs_processed, outputs_processed, contingencies)
    
    return serialized_transaction
    

def createTransactionClaim(input_transaction_hash, input_vout, miner_fee_sats, miner_fee_blocks):
    
    utxo = getUtxo(transaction_hash=input_transaction_hash, vout=input_vout)
    polygon = utxo.get('shape')
    polygon_bytes = polygon.encode('utf-8')
    planet_id = utxo.get('planet_id')
    
    output_keys = generateRandomKeys()
    output_private_key = output_keys[0]
    output_public_key = output_keys[1]

    savePublicPrivateKeysDb(output_private_key, output_public_key)
    
    transaction_version = 2
    transaction_version = transaction_version.to_bytes(2, byteorder = 'big')
        
    #input 1 - claim
    type = 3 
    transaction_hash = input_transaction_hash
    vout = input_vout
    signature = b''
    input_1 = [type.to_bytes(1, byteorder = 'big'), unhexlify(transaction_hash), vout.to_bytes(1, byteorder = 'big'), signature]

    inputs = [input_1]
    
    #output 1 - claim
    type = 3
    planet_id = planet_id
    coordinates = polygon
    public_key = output_public_key
    output_1 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    outputs = [output_1]

    #contingencies
    miner_fee_sats = miner_fee_sats #this is also the claim amount
    miner_fee_blocks = miner_fee_blocks #12960 max 
    transfer_fee_sats = 0
    transfer_fee_blocks = 0 #12960 max
    transfer_fee_address = ''
    contingencies = [miner_fee_sats.to_bytes(6, byteorder = 'big'),
                     miner_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_sats.to_bytes(6, byteorder = 'big'),
                     transfer_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_address.encode('utf-8')
                     ]

    serialized_transaction = serializeTransaction(transaction_version, inputs, outputs, contingencies)
    
    return serialized_transaction    
    

if __name__ == '__main__':

    ############## SIMPLE TRANSACTION #################
    '''
    select 
    '["' || pub_key || '","' || private_key || '","' || st_astext(geom) || '",' || planet_id::varchar || ',' || vout::varchar || ',"' || transaction_hash::varchar || '"]',
        block_id
    from bitland.utxo u
    join wallet.addresses a on u.pub_key = a.public_key 
    order by block_id desc
    '''
    
    transaction_info = ["69ba3b88770d3941a7ca85412df6c33bd3f73e0b9e0e1cad18bff336ce2c3549ce40d2b10f0ccb28cc2b42e786770e16ad4e3b81c86a86a45ed6c95f0beee7a1","43adaf31324eab1251df93692b78a46b10b2b7eadbc409ded9f68c77657ea2a0","POLYGON((-56.793906 85.03956,-56.25 85.03956,-56.25 84.90942,-56.792279 84.90942,-56.793906 85.03956))",1,2,"86a376a1e641a30099a01abdf6f1f18dacd74e08b32c6e95df3c46373a8c07fa"]
    
    input_public_key = transaction_info[0]
    input_private_key = transaction_info[1]
    polygon = transaction_info[2]
    planet_id = transaction_info[3]
    vout = transaction_info[4]
    input_transaction_hash = transaction_info[5]
    input_spend_type = 1
    
    #simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id, input_spend_type)
    #print(hexlify(simple_transaction).decode('utf-8'))
    #print(deserializeTransaction(simple_transaction))
    
    
    ############ MORE COMPLEX TRANSACTION ################
    #INPUTS
    '''
        select 
    '[1,"' || transaction_hash || '",' || vout::varchar || ',"' || pub_key || '","' || private_key || '"]',
        u.id,
        u.block_id
    from bitland.utxo u
    join wallet.addresses a on u.pub_key = a.public_key 
    order by block_id desc
    '''    

   
    input_1 = [1,"d8429ee73601ea61f6472b42ac6cd03a8279da311dc8345971f2e17ac3860df9",0,"257e8da93a727abc057ecade50feaeee08b35c3fb8cfd469ce1f138e9f5beac1d4e8a8a89414c2ba4131707b31661fddec126cdb51a8ac62bd7736629e7e82c5","96cf23d95bec91a39246751eb77faaa47d9e81cf282f5dc8ee747e4313fe3426"]
    input_2 = [1,"8a8b632c30dda4feba350ec4ab3d332dad08260396ad1012aaccd9a285065e5d",0,"085a2f61a47fb122b66e9a341e7425ee2be28024749ea7bc09a43bcbef83117dd424fa0c4c14e9037564a4c3fec687fb82255bffac0e5b14e9f31a7f3057bdbf","25d79c5e076eccaab8881d9ab5c3fc6da3e5724152f82c1b3e90cda567f57c51"]
    input_3 = [1,"c1abd071b9ef14d1a16df7be05e4bf986d9f6eaffb7c260822911b1fe64896a5",0,"ff067b158e11d401e60fd80c4d41e8872fca567662ff96819a9b78b2420cd9c4be5f3e31adc22f62a3546d6f0a6cf0229dcfb6f732879e9b500bdbf6a8bf7679","29a3ebf9bc29031a7a6678906e55a48b976eafba446c0c3b890f3acc1cb909bb"]
    inputs = [input_1,input_2,input_3]
    #inputs = [input_1]
    
    #OUTPUTS
    '''
    with combo as (
    select 
      st_union(geom) as full_geom,
      st_geomfromtext(st_astext(st_geomfromtext('POLYGON((-59.798011780658 85.053067832573, -58.919105530658 84.987149863823, -58.952064515033 84.273038535698, -59.787025452533 84.295011191948, -59.951820374408 84.251065879448, -59.798011780658 85.053067832573))',4326),6),4326) as sub_polygon_1,
      st_geomfromtext(st_astext(st_geomfromtext('POLYGON((-60.632972718158 85.031095176323, -60.358314515033 85.031095176323, -60.391273499408 84.185147910698, -60.589027405658 84.251065879448, -60.654945374408 84.569669395073, -60.632972718158 85.031095176323))',4326),6),4326) as collateral  
    from bitland.utxo
    where id in (548,547,545)
    )  
    --select * from combo
    , intersections as (
    select 
      full_geom,
      st_intersection(full_geom,sub_polygon_1) as sub_polygon_1,
      st_intersection(full_geom,collateral) as collateral
    from combo
    )
    --select * from intersections
    select 
      st_astext(st_difference(st_difference(full_geom,sub_polygon_1),collateral),6) as remainder_polygon,
      st_astext(sub_polygon_1,6) as sub_polygon_1,
      st_astext(collateral,6) as collateral 
    from intersections
    '''
    
    output_1 = [1,1,'MULTIPOLYGON(((-39.375 87.62508,-39.375 87.49116,-40.943756 87.49116,-40.943756 87.7671,-39.375 87.7671,-39.375 87.62508)),((-34.220123 87.7671,-39.375 87.7671,-39.375 87.91884,-34.220123 87.91884,-34.220123 87.7671)))',None]
    output_2 = [1,1,'POLYGON((-40.943756 87.49116,-45 87.49116,-45 87.62508,-45 87.7671,-40.943756 87.7671,-40.943756 87.49116))',None]
    #collateral
    output_3 = [2,1,'POLYGON((-33.75 87.91884,-33.75 87.7671,-34.220123 87.7671,-34.220123 87.91884,-33.75 87.91884))',None]
    outputs = [output_1, output_2, output_3]
    #outputs = [output_1]
    
    #CONTINGENCIES
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    transfer_fee_address_1 = 'bc1qh2kwf0yfrlt3pqs97j5na82t8kdqzq74ycftgn'
    contingencies = [2500,5,3600,6,hexlify(transfer_fee_address_1.encode('utf-8')).decode('utf-8')]
    #contingencies = [0,0,0,0,'']
        
    complex_transaction = createTransaction1(2,inputs,outputs,contingencies)
    print(hexlify(complex_transaction).decode('utf-8'))
    print(deserializeTransaction(complex_transaction))
    
    
    ############ CLAIM TRANSACTION ################
    
    #claim_transaction = createTransactionClaim('4f651474a9f41af5b7d480afdd8ec65730eaaf1872009be993b829a7d69e6bd4', 0, 17500, 350)
    #print(hexlify(claim_transaction).decode('utf-8'))
    
    
    
    
    
    
    
    
    
    