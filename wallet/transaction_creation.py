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
from node.information.transaction import getUtxoInfo
import json

def createSimpleTransactionTransfer(input_transaction_hash, input_vout, input_private_key, input_public_key, polygon, planet_id):
    
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
    type = 4 #standard
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
        
        coordinates = getUtxoInfo(transaction_hash=input_transaction_hash, vout=input_vout).shape
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
    

if __name__ == '__main__':

    #simple transaction
    '''
    select 
    '["' || pub_key || '","' || private_key || '","' || st_astext(geom) || '",' || planet_id::varchar || ',' || vout::varchar || ',"' ||      || '"]',
        block_id
    from bitland.utxo u
    join wallet.addresses a on u.pub_key = a.public_key 
    order by block_id desc
    '''
    
    input_public_key = '700e4f461437fb74f1f0a6fd87b7b7ef3f9311183c71650bef977593d79a49d030bda18cdda096b074218e226694c5e00591b01681c5ff9f44b714ce9848edc3'
    input_private_key = 'f5bfb2b7e46e575dedbfd29be1d2258e5918d35bdd2d210a6d907f01bba5bf40'
    polygon = 'POLYGON((-88.59375 76.35366,-88.59375 76.262552,-88.714027 76.267062,-88.710732 76.1616,-89.296875 76.1616,-89.296875 76.35366,-89.296875 76.478549,-89.156227 76.478549,-89.14924 76.54842,-88.59375 76.54842,-87.890625 76.54842,-87.890625 76.35366,-88.59375 76.35366))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '677d5fc4a0b96d8978fbc50b60ea1b36f53906e26bd83384a2bcd38354f41e4e'
    
    #simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    #print(hexlify(simple_transaction).decode('utf-8'))
    #print(deserialize_transaction(simple_transaction))
    
    
    ############ more complex transaction ################
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
    
    input_1 = [1,"c92ffed21a11db4e5829ce5f027ff09a669aadc78129a6e18432308cdca77ec7",0,"1994ff88d17854fb07d87a89771fc94299dfbdbc5fd3fd2f329ab47092d4b3e5bf219e1616d97f3c66a24b7cdf7dc9296294678aa4bcfb689154a1745363b814","7592a990b5c81f59dedd11bbde952c517c4928bee376008df220922f631d9c4b"]
    input_2 = [1,"36b5f5868ebb7895f4110a3b8a0438d755a0e2c729986ef9ce9f16723f4bed81",0,"e9541b9971f1d0e5c55ab9dad28f0d5c2a83e9374d0a0ad44c0f3c5630868c0db43059f956f32db5481ec387f8097cdba912903f05734e25a37ce7e425849944","5d3f5801da2cc865992585716ad9d6157be2fb771e05bcc14eef958b01dac475"]
    input_3 = [1,"5cc1181c5528c88f4d4a8e5e9c56d43801e7f363d9c2a3140d9dbd59d4ce0d3d",0,"f2eafd84e2e1280dca5cc9d0fa4567d40c5ada78ef59cfa4c73dabb01f015bfc78c1714c4f78b46b5946da4f85c8511bb0764dc2008424f7662caa44cdf4b9e9","953b0999283e367116baf9e0a548c10d67b66bbc5da8d3be972d296cc60dec29"]
    inputs = [input_1,input_2,input_3]
    #inputs = [input_1]
    
    #OUTPUTS
    '''
    select st_union(geom)
    from bitland.utxo
    where id in (159,158,157)    
    
    with combo as (
    select 
      st_union(geom) as full_geom,
      st_geomfromtext('POLYGON((-88.494300843158 76.258822422417, -88.714027405658 76.267062168511, -88.708534241596 76.091280918511, -88.527259827533 76.113253574761, -88.530006409565 76.113253574761, -88.494300843158 76.258822422417))',4326) as sub_polygon_1,
      st_geomfromtext('POLYGON((-89.403419495502 76.478548984917, -89.15622711269 76.478548984917, -89.142494202533 76.61587808648, -89.348487854877 76.59390543023, -89.378700257221 76.54996011773, -89.403419495502 76.478548984917))',4326) as collateral  
    from bitland.utxo
    where id in (159,158,157)
    )    
    , intersections as (
    select 
      full_geom,
      st_intersection(full_geom,sub_polygon_1) as sub_polygon_1,
      st_intersection(full_geom,collateral) as collateral
    from combo
    )
    select 
      st_difference(st_difference(full_geom,sub_polygon_1),collateral) as remainder_polygon,
      sub_polygon_1,
      collateral 
    from intersections
    '''
    
    output_1 = [1,1,'MULTIPOLYGON (((-94.21875 46.6632, -94.21875 46.52964, -94.409135 46.52964, -94.333189 46.6632, -94.21875 46.6632)),((-94.21875 46.2636, -94.21875 46.13094, -94.474127 46.13094, -94.422537 46.2636, -94.21875 46.2636)))',None]
    output_2 = [1,1,'MULTIPOLYGON (((-94.474127 46.13094, -94.570313 46.13094, -94.570313 46.2636, -94.422537 46.2636, -94.474127 46.13094)),((-94.921875 47.33604, -94.921875 47.20086, -95.273438 47.20086, -95.273438 47.33604, -94.921875 47.33604)))',None]
    #collateral
    output_3 = [2,1,'POLYGON ((-94.409135 46.52964, -94.570313 46.52964, -94.570313 46.6632, -94.333189 46.6632, -94.409135 46.52964))',None]
    outputs = [output_1, output_2, output_3]
    #outputs = [output_1]
    
    #CONTINGENCIES
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    transfer_fee_address_1 = 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws'
    contingencies = [50000,2000,50000,2000,hexlify(transfer_fee_address_1.encode('utf-8')).decode('utf-8')]
    #contingencies = [0,0,0,0,'']
        
    complex_transaction = createTransaction1(2,inputs,outputs,contingencies)
    print(hexlify(complex_transaction).decode('utf-8'))
    print(deserialize_transaction(complex_transaction))
    
    