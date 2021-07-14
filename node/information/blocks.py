'''
Created on Jul 12, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from collections import namedtuple


def getMaxBlockHeight():
    
    return executeSql('select * from bitland.max_block;')[0]


def getBlockInformation(block_id = 0, block_header = ''):
    select = ("select id, header_hash , version, prev_block , mrkl_root , time, bits, bitcoin_block_height , miner_bitcoin_address, nonce from bitland.block b "
              +" where id = " + str(block_id) + " or header_hash = '" + str(block_header) + "' ;")
    
    try:
        db_block = executeSql(select)
        columns = namedtuple('columns', ['id', 'header_hash', 'version', 'prev_block', 'mrkl_root', 'time', 'bits', 'bitcoin_block_height', 'miner_bitcoin_address', 'nonce'])
        block = columns(
                        db_block[0],
                        db_block[1],
                        db_block[2],
                        db_block[3],
                        db_block[4],
                        db_block[5],
                        db_block[6],
                        db_block[7],
                        db_block[8],
                        db_block[9]
                        )

    except Exception as error:
        print('no block_found' + str(error))
        block = 'no block_found'
    
    return block 


def getMaxBlockInformation():
    
    max_block = getMaxBlockHeight()
    
    return getBlockInformation(block_id = max_block)


def getBlock(block_id):
    
    query = ('select block from bitland.block_serialized where id = ' + str(block_id) + ';')
    block = executeSql(query)[0]
    
    return block


def getBlocks(start_block_id, end_block_id):
    
    blocks = ''
    
    for i in (start_block_id, end_block_id):
        blocks = blocks + getBlock(i)
        
    return blocks
