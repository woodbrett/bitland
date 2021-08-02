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
    '["' || pub_key || '","' || private_key || '","' || st_astext(geom) || '",' || planet_id::varchar || ',' || vout::varchar || ',"' || transaction_hash::varchar || '"]',
        block_id
    from bitland.utxo u
    join wallet.addresses a on u.pub_key = a.public_key 
    order by block_id desc
    '''
    
    input_public_key = 'aa0ef7f61e9fea10fa562337bcb7c66e2ee2dac2012645a9acdc7b0432d1ee25f9451b16dd11d601e0cb3b4b8eda73d67dfdcf2d530d05163ec2653454f99f1e'
    input_private_key = 'f1a165ed5a2d206f1a9aa0faab0007af4acc72c51348c6b21bcaa4345ffc3ab7'
    polygon = "POLYGON((-22.5 89.74674,-22.5 89.51868,-45 89.51868,-45 89.74674,-22.5 89.74674))"
    planet_id = 1
    vout = 0
    input_transaction_hash = '03aca220f7ec55e458acd9aafadc9af571da0676846fb6d5e2505c82a8849782'
    input_spend_type = 1
    
    #simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id, input_spend_type)
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
    
    input_1 = [1,"a09bf469d5f2f03b6efdc67ed08fc16ffeb0c85a604ad0d8d68df8751878e014",0,"bb975c0184fb17d02277f672816601169783dced038775adf2a9fb6aacd68125f17ad2fe6128d78df685ee1085fdb64513343a899cace23c3f1239e66d9d1814","05c14395a986351bcff7aa05f7c7d2d0f443b588ba3f0f72ebe0f0f9030d59ca"]
    input_2 = [1,"558fa3ff81c645a4136a8fd6ababbe3ae9aeb6c64410f56c85f45a2ff6bdaead",0,"5a3058c716ed7820479fc5e51c0ee2bff83e1003f85f4505766e32db271a0dd9595e6a55e50df4599c6324f950dce46b52c2440af4e523f36db8ffe86b53d6fb","72822e8f5cb71755b40e02f0300641b76541b1fabffeed1e8d783e1f4465beff"]
    input_3 = [1,"5f8c3a04eac19d080c90915fbfde0496f05c7892e8586ca28d9174a974611ec9",0,"b4030ad2dca040e9c05eaad31250f3cf120bccbc97e0914ca664a87ef911734db0bde4dabc6055e94c54679d8bc7fcf27cbe7cd4ba47b6cff8243aad8417d6bd","54a4bf48340d4b518f2fe68793ae78fdfdd3964a75890466cb62bde634a668a9"]
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
    
    output_1 = [1,1,'MULTIPOLYGON(((-59.919629 84.41892,-60.382165 84.41892,-60.363055 84.90942,-59.825561 84.90942,-59.919629 84.41892)),((-56.25 85.31082,-56.25 85.1733,-59.0625 85.1733,-59.0625 85.31082,-56.25 85.31082)))',None]
    output_2 = [1,1,'POLYGON((-59.0625 84.6585,-59.0625 84.41892,-59.919629 84.41892,-59.825561 84.90942,-59.0625 84.90942,-59.0625 84.6585))',None]
    #collateral
    output_3 = [2,1,'POLYGON((-60.382165 84.41892,-60.46875 84.41892,-60.46875 84.6585,-60.46875 84.90942,-60.363055 84.90942,-60.382165 84.41892))',None]
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
    
    