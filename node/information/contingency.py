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