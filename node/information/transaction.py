'''
Created on Jul 24, 2021

@author: brett_wood
'''
from utilities.sql_utils import *
from collections import namedtuple
import json

def getTransaction(transaction_hash = '', id = 0):
    
    transaction_hash = str(transaction_hash)
    id = str(id)
    
    transaction_info = {}
    
    query = ("select id, block_id, transaction_hash, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address, bitcoin_block_height, miner_fee_status, transfer_fee_status, miner_fee_status_block_height, transfer_fee_status_block_height, miner_bitcoin_address " +
             "from bitland.transaction_contingency " +
             "where (transaction_hash = '" + transaction_hash + "' or id = " + id +");"
             )
    
    try:
        transaction = executeSql(query)
        transaction_info = {
            'status':'transaction identified',
            'id': transaction[0], 
            'block_id': transaction[1], 
            'transaction_hash': transaction[2], 
            'version': transaction[3], 
            'is_landbase': transaction[4], 
            'miner_fee_sats': transaction[5], 
            'miner_fee_blocks': transaction[6], 
            'transfer_fee_sats': transaction[7], 
            'transfer_fee_blocks': transaction[8], 
            'transfer_fee_address': transaction[9], 
            'bitcoin_block_height': transaction[10],
            'miner_fee_status': transaction[11], 
            'transfer_fee_status': transaction[12], 
            'miner_fee_status_block_height': transaction[13], 
            'transfer_fee_status_block_height': transaction[14], 
            'miner_bitcoin_address': transaction[15]
        }
        

    except Exception as error:
        transaction_info = {
            'status':'no transaction found',
        }
        
    return transaction_info 


def getTransactionIdByHash(transaction_hash):
    
    select = ("select id from bitland.transaction where transaction_hash = '" + transaction_hash + "';")
    
    transaction_id = executeSql(select)
    return transaction_id


