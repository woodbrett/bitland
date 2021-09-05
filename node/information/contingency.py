'''
Created on Aug 3, 2021

@author: brett_wood
'''
from utilities.sql_utils import *
from collections import namedtuple
        
def getClaim(claimed_output_parcel_id = 0, claim_action_output_parcel_id = 0):
    
    claimed_output_parcel_id = str(claimed_output_parcel_id)
    claim_action_output_parcel_id = str(claim_action_output_parcel_id)
    select = ("select id, claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, invalidation_input_parcel_id, status, claim_end_block, from_bitland_block_height, to_bitland_block_height"
              +" from bitland.active_claim "
              + "where (status = 'LEADING' and claimed_output_parcel_id = " + claimed_output_parcel_id + ") or claim_action_output_parcel_id = " + claim_action_output_parcel_id + ";")

    
    try:
        claim_sql = executeSql(select)
        claim_info = {
            'status':'claim identified',
            'id': claim_sql[0], 
            'claimed_output_parcel_id': claim_sql[1], 
            'claim_action_output_parcel_id': claim_sql[2], 
            'claim_fee_sats': claim_sql[3], 
            'claim_block_height': claim_sql[4], 
            'invalidation_input_parcel_id': claim_sql[5],
            'claim_status': claim_sql[6],
            'claim_end_block': claim_sql[7],
            'from_bitland_block_height': claim_sql[8],
            'to_bitland_block_height': claim_sql[9],
        }
        
    except Exception as error:
        claim_info = {
            'status':'no claim found'
        }
        
    return claim_info     


def getClaims(claimed_output_parcel_id = 0, claim_action_output_parcel_id = 0):
    
    claimed_output_parcel_id = str(claimed_output_parcel_id)
    claim_action_output_parcel_id = str(claim_action_output_parcel_id)
    select = ("select id, claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, leading_claim, invalidated_claim, invalidation_input_parcel_id"
              +" from bitland.claim "
              + "where claimed_output_parcel_id = " + claimed_output_parcel_id + " or claim_action_output_parcel_id = " + claim_action_output_parcel_id + ";")
    
    claim_info = []
    
    try:
        claim_sql = executeSqlMultipleRows(select)
        for i in range(0,len(claim_sql)):
            claim_info.append ({
                'status':'claim identified',
                'id': claim_sql[i][0], 
                'claimed_output_parcel_id': claim_sql[i][1], 
                'claim_action_output_parcel_id': claim_sql[i][2], 
                'claim_fee_sats': claim_sql[i][3], 
                'claim_block_height': claim_sql[i][4], 
                'leading_claim': claim_sql[i][5], 
                'invalidated_claim': claim_sql[i][6], 
                'invalidation_input_parcel_id': claim_sql[i][7]
            })
        
    except Exception as error:
        claim_info = {
            'status':'no claim found'
        }
        
    return claim_info  


def getContingencyStatusDb(transaction_id=0, transaction_hash='', type=''):
    
    transaction_id = str(transaction_id)
    
    select = ("select id, transaction_hash, type, bitcoin_address, fee_sats, fee_blocks, bitland_block, bitcoin_block_height, bitcoin_expiration_height, validation_bitcoin_block_height, validation_address, validation_value, validation_txid, validation_recorded_bitland_block_height"
              +" from bitland.vw_contingency_status "
              + "where (id="+ transaction_id + " or transaction_hash = '" + transaction_hash + "') and type='" + type + "' ;")

    try:
        contingency_sql = executeSql(select)
        contingency_info = {
            'status':'contingency identified',
            'id': contingency_sql[0], 
            'transaction_hash': contingency_sql[1], 
            'type': contingency_sql[2], 
            'bitcoin_address': contingency_sql[3], 
            'fee_sats': contingency_sql[4], 
            'fee_blocks': contingency_sql[5], 
            'bitland_block': contingency_sql[6], 
            'bitcoin_block_height': contingency_sql[7],
            'bitcoin_expiration_height': contingency_sql[8], 
            'validation_bitcoin_block_height': contingency_sql[9], 
            'validation_address': contingency_sql[10],
            'validation_value': contingency_sql[11],
            'validation_txid': contingency_sql[12],
            'validation_recorded_bitland_block_height': contingency_sql[13]
        }
        
    except Exception as error:
        contingency_info = {
            'status':'no contingency found'
        }
    
    return contingency_info


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


def updateExpiredClaims(bitcoin_block_height, confirmation_blocks, bitland_block_height):
    
    bitcoin_block_height = str(bitcoin_block_height)
    confirmation_blocks = str(confirmation_blocks) 
    bitland_block_height = str(bitland_block_height)
    
    query = ("select bitland.update_expired_claims (" + bitcoin_block_height + "," + confirmation_blocks + "," + bitland_block_height + ");")

    update_sql = executeSql(query)
    
    return update_sql


def updateInvalidatedClaims(bitland_block_height):
    
    bitland_block_height = str(bitland_block_height)
    
    query = ("select bitland.update_invalidated_claims (" + bitland_block_height + ");")

    update_sql = executeSql(query)
    
    return update_sql


def updateLeadingClaims(bitland_block_height, claim_blocks, claim_increase):
    
    bitland_block_height = str(bitland_block_height)
    claim_blocks = str(claim_blocks)
    claim_increase = str(claim_increase) 
    
    query = ("select bitland.update_leading_claims (" + bitland_block_height + "," + claim_blocks + "," + claim_increase + ");")

    update_sql = executeSql(query)
    
    return update_sql


def updateSuccessfulClaims(bitland_block_height):
    
    bitland_block_height = str(bitland_block_height)
    
    query = ("select bitland.update_successful_claims (" + bitland_block_height + ");")
    
    update_sql = executeSql(query)
    
    return update_sql    
    
    
def addNewContingenciesDb(bitland_block_height):

    bitland_block_height = str(bitland_block_height)
    
    query = ("select bitland.add_new_contingencies (" + bitland_block_height + ");")
    
    update_sql = executeSql(query)
    
    return update_sql    


def updateContingenciesDb(bitland_block_height, contingency_blocks, bitcoin_block_height):
    
    bitland_block_height = str(bitland_block_height)
    contingency_blocks = str(contingency_blocks)
    bitcoin_block_height = str(bitcoin_block_height) 
    
    query = ("select bitland.update_contingencies (" + bitland_block_height + "," + contingency_blocks + "," + bitcoin_block_height + ");")

    update_sql = executeSql(query)
    
    return update_sql


if __name__ == '__main__':

    print(getContingencyStatusDb(transaction_id=828, type='miner_fee'))
