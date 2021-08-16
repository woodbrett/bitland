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

    serialized_transaction = serialize_transaction(transaction_version, inputs, outputs, contingencies)
    
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

    serialized_transaction = serialize_transaction(transaction_version, inputs_processed, outputs_processed, contingencies)
    
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

    serialized_transaction = serialize_transaction(transaction_version, inputs, outputs, contingencies)
    
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
    
    transaction_info = ["ab331f81a45576b5cc1632b63a47c42349b172a68007c4cb1698fbfcf7b20fa9d42b4a2506b1d86379c84456ae306c768ab0ba3f8a19cb09736b067e6a604b6e","8eee93bc01b4052a57df6d57e70698c57049f73cda2c3897f6c6ff0b09b4cb74","MULTIPOLYGON(((-59.0625 84.6585,-59.0625 84.41892,-60.46875 84.41892,-60.46875 84.6585,-59.0625 84.6585)),((-58.677282 84.6585,-59.0625 84.6585,-59.0625 84.90942,-59.0625 85.03956,-58.615489 85.03956,-58.677282 84.6585)))",1,1,"86a376a1e641a30099a01abdf6f1f18dacd74e08b32c6e95df3c46373a8c07fa"]
    
    input_public_key = transaction_info[0]
    input_private_key = transaction_info[1]
    polygon = transaction_info[2]
    planet_id = transaction_info[3]
    vout = transaction_info[4]
    input_transaction_hash = transaction_info[5]
    input_spend_type = 1
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id, input_spend_type)
    print(hexlify(simple_transaction).decode('utf-8'))
    #print(deserialize_transaction(simple_transaction))
    
    
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
    
    


    
    input_1 = [1,"0e3e9dd6ebd7c566c652b9a022927481e98f71335edf433824839601a9ce6c9c",0,"f644679e9c43223e7c9c550e9838a7f6ce7766aa08cbcab60a3f597ce2d1d5f5760437c918b9d3b8dff64946183ed70c50991ca60a75765502d0f7abc22f5c11","4c248c531c6b8df07eaead7d9e4f2513ee12f607c312ee437b26973b680ec893"]
    input_2 = [1,"282f2cbebae089d3de7074da083807911e40247c780552a9377cb773ac053a09",0,"a7c5d805aa2dfba25499e59c1840d629a0cb51c44bc50fca9fe9ab9139fa15ff7e5fa24ca14de0827a06147d104158e44598bbf004666e8f9aea298f7882de03","85061d709c81c1eb17234d01fb7fd413bfe9a83f19a15fbc01031a91db8baf84"]
    input_3 = [1,"14247b34415fb7982dd74141dd5070b5e3c230b8ff32aa5f77e0027f7b04464b",0,"77518b2b01ad8fdb4495483262a60dc58a999bbbaff6671435c8d200905b8ea1b14f3f556cf6ab74793878e3d1fa3b45040f8998ae3f2c06f32c128c8701c2b5","4f2f5b877eb85b31a1cc2291efefbc4b3cb04e3bfd7a7271b70d755e4a46d1d4"]
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
    
    output_1 = [1,1,'POLYGON((-57.65625 84.90942,-57.65625 84.6585,-58.677282 84.6585,-58.615489 85.03956,-56.793906 85.03956,-56.792279 84.90942,-57.65625 84.90942))',None]
    output_2 = [1,1,'MULTIPOLYGON(((-59.0625 84.6585,-59.0625 84.41892,-60.46875 84.41892,-60.46875 84.6585,-59.0625 84.6585)),((-58.677282 84.6585,-59.0625 84.6585,-59.0625 84.90942,-59.0625 85.03956,-58.615489 85.03956,-58.677282 84.6585)))',None]
    #collateral
    output_3 = [2,1,'POLYGON((-56.793906 85.03956,-56.25 85.03956,-56.25 84.90942,-56.792279 84.90942,-56.793906 85.03956))',None]
    outputs = [output_1, output_2, output_3]
    #outputs = [output_1]
    
    #CONTINGENCIES
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    transfer_fee_address_1 = 'bc1qh2kwf0yfrlt3pqs97j5na82t8kdqzq74ycftgn'
    contingencies = [41010,100,13052,100,hexlify(transfer_fee_address_1.encode('utf-8')).decode('utf-8')]
    #contingencies = [0,0,0,0,'']
        
    complex_transaction = createTransaction1(2,inputs,outputs,contingencies)
    print(hexlify(complex_transaction).decode('utf-8'))
    print(deserialize_transaction(complex_transaction))
    
    
    ############ CLAIM TRANSACTION ################
    
    #claim_transaction = createTransactionClaim('4f651474a9f41af5b7d480afdd8ec65730eaaf1872009be993b829a7d69e6bd4', 0, 17500, 350)
    #print(hexlify(claim_transaction).decode('utf-8'))
    
    
    
    
    
    
    
    
    
    