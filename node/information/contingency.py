'''
Created on Aug 3, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from collections import namedtuple
        
def getClaim(claimed_output_parcel_id = 0, claim_action_output_parcel_id = 0):
    
    claimed_output_parcel_id = str(claimed_output_parcel_id)
    claim_action_output_parcel_id = str(claim_action_output_parcel_id)
    select = ("select id, claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, leading_claim, invalidated_claim, invalidation_input_parcel_id"
              +" from bitland.claim "
              + "where (leading_claim = true and claimed_output_parcel_id = " + claimed_output_parcel_id + ") or claim_action_output_parcel_id = " + claim_action_output_parcel_id + ";")
    
    try:
        claim_sql = executeSql(select)
        claim_info = {
            'status':'claim identified',
            'id': claim_sql[0], 
            'claimed_output_parcel_id': claim_sql[1], 
            'claim_action_output_parcel_id': claim_sql[2], 
            'claim_fee_sats': claim_sql[3], 
            'claim_block_height': claim_sql[4], 
            'leading_claim': claim_sql[5], 
            'invalidated_claim': claim_sql[6], 
            'invalidation_input_parcel_id': claim_sql[7]
        }
        
    except Exception as error:
        claim_info = {
            'status':'no claim found'
        }
        
    return claim_info     


#UPDATE - may be more elegant to get transactions from that table vs distincting UTXOs
def getExpiringCollateralTransactions(bitcoin_block_id):
    select = ("select id from bitland.transaction_contingency where miner_fee_sats <> 0 and miner_fee_status is null and bitcoin_block_height + miner_fee_blocks < " + str(bitcoin_block_id) + ";")
    return executeSqlMultipleRows(select)


def getExpiringTransferFeeTransactions(bitcoin_block_id):
    select = ("select id from bitland.transaction_contingency where transfer_fee_sats <> 0 and transfer_fee_status is null and bitcoin_block_height + miner_fee_blocks < " + str(bitcoin_block_id) + ";")
    return executeSqlMultipleRows(select)
    

#UPDATE to change to dict if this ends up getting used
def getContingencyStatus(output_id):
    output_id = str(output_id)
    select = ("select status, output_parcel_id, output_parcel_type, contingency_transaction_id, contingency_fee_vout, contingency_block_height, recorded_status_bitcoin_block_height ,recorded_status_bitland_block_height from bitland.contingency_status where output_parcel_id = " + str(output_id) + ";")
    
    try:
        contingency_sql = executeSql(select)
        columns = namedtuple('columns', ['status', 'output_parcel_id', 'output_parcel_type', 'contingency_transaction_id', 'contingency_fee_vout', 'contingency_block_height', 'recorded_status_bitcoin_block_height', 'recorded_status_bitland_block_height'])
        contingency_output = columns(
                        contingency_sql[0],
                        contingency_sql[1],
                        contingency_sql[2],
                        contingency_sql[3],
                        contingency_sql[4],
                        contingency_sql[5],
                        contingency_sql[6],
                        contingency_sql[7]
                        )
        
    except Exception as error:
        print('no contingency record found for output' + str(error))
        columns = namedtuple('columns', ['status'])
        contingency_output = columns(
                        'no contingency db records for output')
    
    return contingency_output  
      