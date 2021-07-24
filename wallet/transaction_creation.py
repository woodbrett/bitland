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


def createTransaction1(transaction_version, inputs, outputs, contingencies):
    #inputs [input_version, input_transaction_hash, input_vout, input_private_key, input_public_key]
    #outputs [output_version, planet, shape, public_script (address)]
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    
    inputs_processed = []
    outputs_processed = []
    transaction_version = 2
    transaction_version = transaction_version.to_bytes(2, byteorder = 'big')
    
    for i in range(0,len(inputs)):  
    
        input_version = inputs[i][0]
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
        type = 1 #standard
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
    
    input_public_key = '2f499fc81d1fac1018ecc5e35d971f5e38c9507de0a3faa78da21cd5f22deb130ea38f96bbccc791c1b91765442a157a92142f8cd5ccf135bbcb7a20d05f5322'
    input_private_key = '403c06b0f058d7f242aca5901ecb951ae4d41a9c02ff2ca96ca29c71c130f29c'
    polygon = 'POLYGON((-39.375 87.7671, -39.375 87.62508, -45 87.62508, -45 87.7671, -39.375 87.7671))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '3c75b4c2a69b3a86e13ac62705a6cf2d8a56d7d8b8d18bf846c621d62478fe06'
    
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
    
    input_1 = [1,"5133603c845ab7d0268c85bec310e002aefdedf9bd83fb189dc79c2fc3abbfaf",0,"700e4f461437fb74f1f0a6fd87b7b7ef3f9311183c71650bef977593d79a49d030bda18cdda096b074218e226694c5e00591b01681c5ff9f44b714ce9848edc3","f5bfb2b7e46e575dedbfd29be1d2258e5918d35bdd2d210a6d907f01bba5bf40"]
    input_2 = [1,"5814c128aff69a595762d1ce28ded5f86e0ae840951bcc61e493bd6aa6878d2e",0,"8a94ddd556a31782f5d8e6496fab8363820bc316c7889886e704a5bf47c902dfdf5e7432c63fc4f68f6861508050fd9788a4ad537bc269b16647124fab24c575","c50b24d29a6408a1c74b3c4f21d6559f4cb7e39a63f561e275ac9359b0816175"]
    input_3 = [1,"9f6870bf482a445cf102596a55efd1ff1a35edec9dcd425cf0f3cf4478aa2e25",0,"8e44106cc7718202ffa0180ca9d84645f680f5da89c3cbd3ab045a2124de37499401534fc55da398ee4d9f0267966f80d016a7b7902af62d0342a87640c94b7f","665b2c0e6d372c9b4bd060376263b7558a43bea963dc8ea0adedba3fb8375904"]
    inputs = [input_1,input_2,input_3]
    
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
    
    output_1 = [1,1,'POLYGON ((-88.59375 76.35366, -88.59375 76.26255176579869, -88.714027405658 76.267062168511, -88.71073171289233 76.1616, -89.296875 76.1616, -89.296875 76.35366, -89.296875 76.478548984917, -89.15622711269 76.478548984917, -89.14924001118135 76.54842, -88.59375 76.54842, -87.890625 76.54842, -87.890625 76.35366, -88.59375 76.35366))',None]
    output_2 = [1,1,'POLYGON ((-88.59375 76.26255176579869, -88.59375 76.1616, -88.71073171289233 76.1616, -88.714027405658 76.267062168511, -88.59375 76.26255176579869))',None]
    #collateral
    output_3 = [2,1,'POLYGON ((-89.296875 76.478548984917, -89.296875 76.54842, -89.14924001118135 76.54842, -89.15622711269 76.478548984917, -89.296875 76.478548984917))',None]
    outputs = [output_1, output_2, output_3]
    
    #CONTINGENCIES
    #contingencies [miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address]
    transfer_fee_address_1 = '1GX28yLjVWux7ws4UQ9FB4MnLH4UKTPK2z'
    contingencies = [50000,100,50000,100,hexlify(transfer_fee_address_1.encode('utf-8')).decode('utf-8')]
        
    #complex_transaction = createTransaction1(2,inputs,outputs,contingencies)
    #print(hexlify(complex_transaction).decode('utf-8'))
    #print(deserialize_transaction(complex_transaction))
    
    '000203015133603c845ab7d0268c85bec310e002aefdedf9bd83fb189dc79c2fc3abbfaf004066264218daad0dac040412be6dda4d862c58a8a3d3491acfe0c77bf58b12859d1b0699a5a79d8d921a9f0eb21540d921f742dbcda02f5238a41d69bd033901fc015814c128aff69a595762d1ce28ded5f86e0ae840951bcc61e493bd6aa6878d2e004076251c18337b5ad0649bdcb02aac257e6cd57a7abc9762629b7c049874fe71539fdcc4c15771b6a0b59c66e81ccfad6967622fcfbfc3e5eb72634db7fc041c70019f6870bf482a445cf102596a55efd1ff1a35edec9dcd425cf0f3cf4478aa2e2500406f208cf7d15ed71e052b14e9bf23187ce69b3d122a278a8a1b1e9066c26dd0abd5c7cdddfaff67f6e57a2b0721a19844e3793a35fb33a223e2eeb61e008a76e00301010141504f4c59474f4e28282d38382e35393337352037362e33353336362c2d38382e35393337352037362e32363235353137363537393836392c2d38382e3731343032373430353635382037362e3236373036323136383531312c2d38382e37313037333137313238393233332037362e313631362c2d38392e3239363837352037362e313631362c2d38392e3239363837352037362e33353336362c2d38392e3239363837352037362e3437383534383938343931372c2d38392e31353632323731313236392037362e3437383534383938343931372c2d38392e31343932343030313131383133352037362e35343834322c2d38382e35393337352037362e35343834322c2d38372e3839303632352037362e35343834322c2d38372e3839303632352037362e33353336362c2d38382e35393337352037362e33353336362929408df9560d48f67fe122679245430635553b37f6860a3b261ef504a4df19286f90c46a6452606a56fa569db1edd85a282df3513afce43aaef9eb87f97bb457789c01010090504f4c59474f4e28282d38382e35393337352037362e32363235353137363537393836392c2d38382e35393337352037362e313631362c2d38382e37313037333137313238393233332037362e313631362c2d38382e3731343032373430353635382037362e3236373036323136383531312c2d38382e35393337352037362e32363235353137363537393836392929400cffde9bb11a7778d10b32582a208a4674fef749bbcc815c9fa9297b4d54025134dd56ba003697ff57f0493debd003e45431d275aabb9fdf2f8f4a3fb46c358402010090504f4c59474f4e28282d38392e3239363837352037362e3437383534383938343931372c2d38392e3239363837352037362e35343834322c2d38392e31343932343030313131383133352037362e35343834322c2d38392e31353632323731313236392037362e3437383534383938343931372c2d38392e3239363837352037362e343738353438393834393137292940f10bdaab7272758c8d8507e337bf8f4f917716c5852dc61419832a39c2ec96a6a770142d44ff2cba814caf201f781b0c9232d4ed918b1d07a0ef5e837fc55f7b00000000c350006400000000c3500064443331343735383332333837393463366135363537373537383337373737333334353535313339343634323334346436653463343833343535346235343530346233323761'
    