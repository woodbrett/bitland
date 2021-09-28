'''
Created on Feb 24, 2021

@author: brett_wood
'''
from utilities.sql_utils import executeSql
from node.blockchain.transaction_serialization import serializeTransaction
from wallet.key_generation import *
from system_variables import mining_path

def getLandbaseTransaction():
    
    return populateLandbaseTransaction(desiredLandbase())


def desiredLandbase():

    path = mining_path
    
    query_find_desired_landbase = ("select st_astext(geom) as landbase "
        + "from bitland.landbase_enum le "
        + "where st_intersects( "
          + "le.geom, " 
          + "st_geomfromtext('" + path + "',4326) ) "
          + "and valid_claim = true "
        + "limit 1 " )    

    query_pick_random_landbase = ("select st_astext(geom) as landbase from bitland.landbase_enum le where valid_claim = true limit 1 ")
    
    try:
        landbase = executeSql(query_find_desired_landbase)[0]
    
    except:
        try: 
            landbase = executeSql(query_pick_random_landbase)[0]
        except:
            print("couldn't find landbase from path ")
            landbase = 'unable to find desired landabse'
        
    return landbase
    

def populateLandbaseTransaction(landbase):

    keys = generateRandomKeys()

    savePublicPrivateKeysDb(keys.get('private_key'), keys.get('public_key'))

    version = 1
    inputs = []
    output_version = 0
    output_1_planet = 1
    output_1_shape = landbase
    output_1_script = keys.get('public_key')
    contingencies = []
    
    version_bytes = version.to_bytes(2, byteorder = 'big')
    inputs_bytes = inputs
    output_1_version_bytes = output_version.to_bytes(1, byteorder = 'big')
    output_1_planet_bytes = output_1_planet.to_bytes(1, byteorder = 'big')
    output_1_shape_bytes = output_1_shape.encode('utf-8')
    output_1_script_bytes = unhexlify(output_1_script)
    output_1_bytes = [output_1_version_bytes,output_1_planet_bytes,output_1_shape_bytes,output_1_script_bytes]
    outputs_bytes = [output_1_bytes]
    
    miner_fee_sats = 0 #100000000000
    miner_fee_blocks = 0 #12960 #12960 max
    transfer_fee_sats = 0 #2000000000000
    transfer_fee_blocks = 0 #1000 #12960 max
    transfer_fee_address = '' 
    contingencies_bytes = [miner_fee_sats.to_bytes(6, byteorder = 'big'),
                     miner_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_sats.to_bytes(6, byteorder = 'big'),
                     transfer_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_address.encode('utf-8')
                     ]
    
    serialized_transaction = serializeTransaction(
        version_bytes, #version
        inputs_bytes, #inputs
        outputs_bytes, #outputs
        contingencies_bytes #contingencies
        )
    
    return serialized_transaction

