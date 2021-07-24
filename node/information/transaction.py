'''
Created on Jul 24, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from collections import namedtuple
import json

def getUtxoInfo (transaction_hash = '', vout = 0, id = 0):
    
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
        columns = namedtuple('columns', ['planet_id', 'shape', 'pub_key', 'id', 'vout', 'transaction_hash', 'transaction_id', 'block_id', 'miner_fee_sats', 'miner_fee_blocks', 'transfer_fee_sats', 'transfer_fee_blocks', 'transfer_fee_address', 'bitcoin_block_height', 'miner_bitcoin_address', 'miner_landbase_address', 'output_version', 'transfer_fee_failover_address', 'claim_fee_sats', 'claim_block_height', 'miner_fee_status', 'transfer_fee_status', 'miner_fee_status_block_height', 'transfer_fee_status_block_height'])
        utxo_output = columns(
                        output_parcel[0],
                        output_parcel[1],
                        output_parcel[2],
                        output_parcel[3],
                        output_parcel[4],
                        output_parcel[5],
                        output_parcel[6],
                        output_parcel[7],
                        output_parcel[8],
                        output_parcel[9],
                        output_parcel[10],
                        output_parcel[11],
                        output_parcel[12],
                        output_parcel[13],
                        output_parcel[14],
                        output_parcel[15],
                        output_parcel[16],
                        output_parcel[17],
                        output_parcel[18],
                        output_parcel[19],
                        output_parcel[20],
                        output_parcel[21],
                        output_parcel[22],
                        output_parcel[23]
                        )

    except Exception as error:
        print('no utxo found' + str(error))
        utxo_output = 'no matched utxo'
    
    return utxo_output 