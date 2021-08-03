'''
Created on Aug 3, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from collections import namedtuple
import json

def getUtxo (transaction_hash = '', vout = 0, id = 0):
    
    transaction_hash = str(transaction_hash)
    vout = str(vout)
    id = str(id)
    
    query = ("select planet_id, st_astext(geom) as shape, pub_key, id, vout, transaction_hash, transaction_id, block_id, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address, bitcoin_block_height, miner_bitcoin_address, miner_landbase_address, output_version, transfer_fee_failover_address, claim_fee_sats, claim_block_height, miner_fee_status, transfer_fee_status, miner_fee_status_block_height, transfer_fee_status_block_height " +
             "from bitland.utxo " +
             "where (transaction_hash = '" + transaction_hash + "'" +
             "  and vout = " + vout + ") or id = " + id
             )
    
    try:
        output_parcel = executeSql(query)
        utxo_output = {
            'status':'utxo identified',
            'planet_id': output_parcel[0], 
            'shape': output_parcel[1], 
            'pub_key': output_parcel[2], 
            'id': output_parcel[3], 
            'vout': output_parcel[4], 
            'transaction_hash': output_parcel[5], 
            'transaction_id': output_parcel[6], 
            'block_id': output_parcel[7], 
            'miner_fee_sats': output_parcel[8], 
            'miner_fee_blocks': output_parcel[9], 
            'transfer_fee_sats': output_parcel[10], 
            'transfer_fee_blocks': output_parcel[11], 
            'transfer_fee_address': output_parcel[12], 
            'bitcoin_block_height': output_parcel[13], 
            'miner_bitcoin_address': output_parcel[14], 
            'miner_landbase_address': output_parcel[15], 
            'output_version': output_parcel[16], 
            'transfer_fee_failover_address': output_parcel[17], 
            'claim_fee_sats': output_parcel[18], 
            'claim_block_height': output_parcel[19], 
            'miner_fee_status': output_parcel[20], 
            'transfer_fee_status': output_parcel[21], 
            'miner_fee_status_block_height': output_parcel[22], 
            'transfer_fee_status_block_height': output_parcel[23]
        }

    except Exception as error:
        utxo_output = {
            'status':'no utxo found'
        }
        
    return utxo_output 




