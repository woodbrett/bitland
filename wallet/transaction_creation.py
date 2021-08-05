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

    input_public_key = 'af6d999747d695f7a21370cb2cee05b3e49182219ba6eee24e1e35576be0d719aa995e98fe10288e0937921b98fa806378b511506794d80f8f6a1a7ca2e52124'
    input_private_key = '7e01de010c7f5903f0625006f73fb190307315d7da11746688aa52af24c9f715'
    polygon = "POLYGON((-60.382165 84.41892,-60.46875 84.41892,-60.46875 84.6585,-60.46875 84.90942,-60.363055 84.90942,-60.382165 84.41892))"
    planet_id = 1
    vout = 2
    input_transaction_hash = 'a8788b7873e8c5671d62c2f3936b34ec3207bfc68062ea4250e4b10182dd8845'
    input_spend_type = 1
    
    #simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id, input_spend_type)
    #print(hexlify(simple_transaction).decode('utf-8'))
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
    
    input_1 = [1,"e43170fb0ce4584874ddc87f57832ed544e20f4391ac81d45f12a557f82ad981",0,"7eaacc77cc4fcdf2c5317eff07bade1ce572ff2eb8c8f07bdc39b797e6e36b82f6c0f5cd0d3d17eb394d01e203d6ffa873b6c9c752340e9a6e498f470c5fe429","1e5a95b46e5f222b1e4f10fae4a51872d11eee35f9c4d3c5ab11ff21ad059c6e"]
    input_2 = [1,"9991247337d7d2083cb3015bbddc901203d7c6457dd92ecd2fffa96b9a4d6297",0,"ef70cb3ede3f61210f1c6c030b22f969e3413a29c3f03b16baf579e409e6e2267b1e7abc519fabc08624d620aeebee0da462198ef1b8948a36ec3d09049e6041","60f4ef52fd77f5e4433db9af0b0136ef3b46b0159dd7bb7f967ef958f0174867"]
    input_3 = [1,"5d9b93ab7d15bf0b21ddb025c454b757032d9fc6eda6cdb2f505a7a9f07c7a5c",0,"69022ccf1a0644a5e07eb2f89b3e9ab217fcc158f3525655a2a30f66c0c61a916858846f55db7172d5e71e3399d18fc191f0efc9b1fa12efcaeab17e0bbe27db","9d71aea112309b1f64af8d06b1c2d6198bf74c1c850e43cc615c7d738ebe0146"]
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
    
    output_1 = [1,1,'MULTIPOLYGON(((-56.25 85.1733,-56.25 85.03956,-59.0625 85.03956,-59.0625 85.1733,-56.25 85.1733)),((-45 87.01524,-45 86.80374,-45.424322 86.80374,-45.289507 87.01524,-45 87.01524)),((-45.928667 86.80374,-47.8125 86.80374,-47.8125 87.01524,-45.835072 87.01524,-45.928667 86.80374),(-46.673584 86.955708,-46.657105 86.900777,-46.662598 86.856832,-46.26709 86.878804,-46.300049 86.977681,-46.673584 86.955708)),((-22.5 89.74674,-22.5 89.51868,-43.693747 89.51868,-43.548375 89.74674,-22.5 89.74674)),((-44.727228 89.51868,-45 89.51868,-45 89.74674,-44.626304 89.74674,-44.727228 89.51868)))',None]
    output_2 = [1,1,'POLYGON((-46.673584 86.955708,-46.300049 86.977681,-46.26709 86.878804,-46.662598 86.856832,-46.657105 86.900777,-46.673584 86.955708))',None]
    #collateral
    output_3 = [2,1,'MULTIPOLYGON(((-45.424322 86.80374,-45.928667 86.80374,-45.835072 87.01524,-45.289507 87.01524,-45.424322 86.80374)),((-43.693747 89.51868,-44.727228 89.51868,-44.626304 89.74674,-43.548375 89.74674,-43.693747 89.51868)))',None]
    outputs = [output_1, output_2, output_3]
    #outputs = [output_1]
    
    #CONTINGENCIES
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    transfer_fee_address_1 = 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws'
    contingencies = [50001,2000,50001,2000,hexlify(transfer_fee_address_1.encode('utf-8')).decode('utf-8')]
    #contingencies = [0,0,0,0,'']
        
    #complex_transaction = createTransaction1(2,inputs,outputs,contingencies)
    #print(hexlify(complex_transaction).decode('utf-8'))
    #print(deserialize_transaction(complex_transaction))
    
    
    ############ CLAIM TRANSACTION ################
    
    claim_transaction = createTransactionClaim('11e0177991e5b50d90c1e3492c5d8b2cae1fa2c1d0fdd856a96458682f859cfa', 0, 35000, 350)
    print(hexlify(claim_transaction).decode('utf-8'))
    
    
    
    
    
    
    
    
    
    