'''
Created on Jul 12, 2021

@author: brett_wood
'''
from utilities.sql_utils import *
from collections import namedtuple
import json

def getMaxBlockHeight():
    
    return executeSql('select * from bitland.max_block;')[0]


def getMaxBlockInformation():
    
    max_block = getMaxBlockHeight()
    
    return getBlock(block_id = max_block)


def getBlocksSerialized(start_block_id, end_block_id):
    
    blocks = []
    
    for i in range(start_block_id, end_block_id + 1): #+1 to make it inclusive
        
        blocks.append([i,getBlockSerialized(i)])
    
    return blocks


def getBlockCount():
    
    query = ("select count(*) from bitland.block b where id > 0")
    block_count = executeSql(query)[0]
    return block_count


def getPrevBlock():
    
    query = ("select header_hash, id " 
                              + "from bitland.block b "
                              + "join bitland.max_block mb on b.id = mb.max_block" ) 
    prev_block = executeSql(query)[0]
    
    return prev_block 


def getMaxBlock():

    return executeSql('select * from bitland.max_block;')[0]


def getPriorBlock():
    
    max_block = getMaxBlock()
    select = ('select header_hash, bits, id from bitland.block b where id = ' + str(max_block) + ';')
    return executeSql(select)


def getBlock(block_id = -1, header_hash = ''):
    select = ("select id, header_hash , version, prev_block , mrkl_root , time, bits, bitcoin_block_height , miner_bitcoin_address, nonce, bitcoin_hash, bitcoin_last_64_mrkl from bitland.block b "
              +" where id = " + str(block_id) + " or header_hash = '" + str(header_hash) + "' ;")
    
    try:
        db_block = executeSql(select)
        block = {
            'status': 'block identified',
            'id': db_block[0], 
            'header_hash': db_block[1], 
            'version': db_block[2], 
            'prev_block': db_block[3], 
            'mrkl_root': db_block[4], 
            'time': db_block[5], 
            'bits': db_block[6], 
            'bitcoin_block_height': db_block[7], 
            'miner_bitcoin_address': db_block[8], 
            'nonce': db_block[9],
            'bitcoin_hash': db_block[10], 
            'bitcoin_last_64_mrkl': db_block[11]
        }

    except Exception as error:
        block = {
            'status': 'no block found',
        }    

    return block 


def getBlockSerialized(block_id):
    
    select = ("select block from bitland.block_serialized where id = " +str(block_id))

    try:
        block = executeSql(select)[0]
        
    except Exception as error:
        block = 'no block found'  

    return block 


def getBlockHeaders(start_block_height, end_block_height):
    
    start_block_height = str(start_block_height)
    end_block_height = str(end_block_height)
    select = ("select header_hash from bitland.block where id between " + start_block_height + " and " + end_block_height + " ;")
    return executeSqlMultipleRows(select)


def getMedianBlockTime11():
    
    select = ("with max_id as ("
        "\n select max(id) as max_id from bitland.block"
        "\n )"
        "\n select PERCENTILE_CONT(0.5) within group(ORDER BY b.time)"
        "\n from max_id m"
        "\n join bitland.block b on b.id >= (m.max_id - 10)")
    
    median_time_11 = executeSql(select)[0]

    return median_time_11


def getKmlLandbaseByBlock(block_id):
    
    select = ("select " +
              "'<kml xmlns=\"http://www.opengis.net/kml/2.2\"><Document><Style id=\"polygon_1\"><LineStyle><color>ff0000ff</color><width>5.5</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style><Placemark><styleUrl>#polygon_1</styleUrl>'" + 
              " || st_askml(geom) " +
              " || '</Placemark></Document></kml>' " +
              " from bitland.utxo where block_id = " +
              str(block_id) + " and output_version = 0;")
    
    print(select)
    
    kml = executeSql(select)[0]

    return kml

