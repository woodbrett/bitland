'''
Created on Jul 13, 2021

@author: brett_wood
'''
from utilities.sql_utils import *
from collections import namedtuple
import json

def getMempoolInformation(id=0, transaction_hash=''):
    select = ("select id, transaction_hash , is_landbase , miner_fee_sats, miner_fee_blocks , transfer_fee_sats , transfer_fee_blocks , transfer_fee_address from bitland.transaction_mempool"
              +" where id = " + str(id) + " or transaction_hash = '" + str(transaction_hash) + "' ;")
    
    try:
        db_block = executeSql(select)
        columns = namedtuple('columns', ['id', 'transaction_hash', 'is_landbase', 'miner_fee_sats', 'miner_fee_blocks', 'transfer_fee_sats', 'transfer_fee_blocks', 'transfer_fee_address'])
        block = columns(
                        db_block[0],
                        db_block[1],
                        db_block[2],
                        db_block[3],
                        db_block[4],
                        db_block[5],
                        db_block[6],
                        db_block[7]
                        )

    except Exception as error:
        print('no_transaction_found' + str(error))
        block = 'no_transaction_found'
    
    return block 