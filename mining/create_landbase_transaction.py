'''
Created on Feb 24, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSql
from node.blockchain.transaction_serialization import serialize_transaction
from wallet.key_generation import *

def getLandbaseTransaction():
    
    return populateLandbaseTransaction(desiredLandbase())


def desiredLandbase():

    path = 'LINESTRING(-24.32582123586823 89.84080925775434, -74.62860694880915 82.52182923327297, -91.10241210722151 75.38399911209015, -95.0423241796008 66.86026257852093, -100.6851598368639 54.57263922226819)'
    
    query_find_desired_landbase = ("select st_astext(geom) as landbase "
        + "from landbase_enum le "
        + "where st_intersects( "
          + "le.geom, " 
          + "st_geomfromtext('" + path + "',4326) ) "
          + "and valid_claim = true "
        + "limit 1 " )    

    query_pick_random_landbase = ("select st_astext(geom) as landbase from landbase_enum le where valid_claim = true limit 1 ")
    
    print(query_pick_random_landbase)
    
    try:
        landbase = executeSql(query_find_desired_landbase)[0]
    
    except Exception as error:
        print("couldn't find landbase from path ")
        landbase = 'unable to find desired landabse'
        
    return landbase
    

def populateLandbaseTransaction(landbase):

    keys = generateRandomKeys()
    private_key = keys[0]
    public_key = keys[1]

    savePublicPrivateKeysDb(private_key, public_key)

    version = 1
    inputs = []
    output_version = 0
    output_1_planet = 1
    output_1_shape = landbase
    output_1_script = public_key
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
    
    serialized_transaction = serialize_transaction(
        version_bytes, #version
        inputs_bytes, #inputs
        outputs_bytes, #outputs
        contingencies_bytes #contingencies
        )
    
    return serialized_transaction


if __name__ == '__main__':

    print(desiredLandbase())

    landbase = 'POLYGON((-22.5 89.74674,-22.5 89.51868,-45 89.51868,-45 89.74674,-22.5 89.74674))'
    public_key = '027c5ef9bc2b7b169cde0327fc08883e0d4e2a603f2c6a47c08b75fe79df0e88742e461b2a3956d15467d253455dae6737ea2f22de440fc2923f3d1c592cc1d1'
    
    version = 1
    inputs = []
    output_1_planet = 1
    output_1_shape = landbase
    output_1_script = public_key
    contingencies = []
    claims = []
    
    version_bytes = version.to_bytes(2, byteorder = 'big')
    inputs_bytes = inputs
    output_1_planet_bytes = output_1_planet.to_bytes(1, byteorder = 'big')
    output_1_shape_bytes = output_1_shape.encode('utf-8')
    output_1_script_bytes = output_1_script.encode('utf-8')
    output_1_bytes = [output_1_planet_bytes,output_1_shape_bytes,output_1_script_bytes]
    outputs_bytes = [output_1_bytes]
    contingencies_bytes = contingencies
    claims_bytes = claims
    
    serialized_transaction = serialize_transaction(
        version_bytes, #version
        inputs_bytes, #inputs
        outputs_bytes, #outputs
        contingencies_bytes, #contingencies
        claims_bytes #claims
        )
    
    print(serialized_transaction)
    print(hexlify(serialized_transaction).decode('utf-8'))
    
    print(hexlify(getLandbaseTransaction()).decode('utf-8'))
