'''
Created on Mar 11, 2021

@author: brett_wood
'''
from collections import namedtuple
import requests
from system_variables import address_search_url
from node.blockchain.global_variables import *
from node.information.utxo import (
    getUtxo
    )
from node.information.transaction import (
    getTransaction
    )
from node.information.contingency import (
    getClaim, getContingencyStatusDb, getClaims, updateExpiredClaims,
    updateInvalidatedClaims, updateLeadingClaims, updateSuccessfulClaims,
    addNewContingenciesDb, updateContingenciesDb
    )
from utilities.sql_utils import executeSql

#UPDATE provide more info when an output isnt found (e.g. rather than just no matched utxo, say that it was claimed or spent etc)
def inspectParcel(transaction, vout, bitcoin_block_height, bitland_block):
    
    output_parcel = getUtxo(transaction_hash=transaction, vout=vout)
    
    if output_parcel.get('status') == 'no matched utxo':
        is_current_utxo = False
        type = None
        miner_fee_status = None
        transfer_fee_status = None
        outstanding_claims = None
        claim_status = None
    
    else:
        output_parcel_bitcoin_block_height = output_parcel.get('bitcoin_block_height')
        
        is_current_utxo = True
        type = output_parcel.get('output_version')
        miner_fee_status = output_parcel.get('miner_fee_status') #get the status of the miner fee associated with the utxo - if no miner fee then it returns NO_CONTINGENCY
        transfer_fee_status = output_parcel.get('transfer_fee_status') #get status of the transfer fee associated with the utxo - if no transfer fee then it returns NO_CONTINGENCY
        outstanding_claims = output_parcel.get('claim_on_parcel') #find claims associated with the UTXO
        claim_status = output_parcel.get('claim_status') #get the status of the claim transaction (if it is a claim UTXO)
        
    parcel_output = {
        'is_current_utxo': is_current_utxo, 
        'type': type, 
        'miner_fee_status': miner_fee_status, 
        'transfer_fee_status': transfer_fee_status, 
        'outstanding_claims': outstanding_claims, 
        'claim_status': claim_status
    }
    
    return parcel_output


def updateContingencies(bitland_block_height, confirmation_blocks, bitcoin_block_height):
    
    #ENUMERATION OF CONTINGENCY STATES:
    #OPEN
    #EXPIRED_CONFIRMED
    #EXPIRED_UNCONFIRMED
    #VALIDATED_CONFIRMED
    #VALIDATED_UNCONFIRMED
    #NO_CONTINGENCY
    
    #add new entries for new transactions
    add_new_contingencies = addNewContingenciesDb(bitland_block_height)
    
    #update contingencies that succeeeded and update contingencies that failed
    update_contingencies = updateContingenciesDb(bitland_block_height, confirmation_blocks, bitcoin_block_height)
    
    return True


################CLAIM CALCULATIONS AND DB OPERATIONS
def updateClaims(bitcoin_block_height, confirmation_blocks, bitland_block_height, claim_blocks, claim_increase):

    #ENUMERATION OF CLAIM STATES:
    #OPEN
    #EXPIRED
    #SUPERCEDED
    #LEADING
    #INVALIDATED
    #SUCCESSFUL
    
    #UPDATE - move the logic to add the claim to the bitland.claim table to this function
    
    #update claims where miner fee/transfer fee expired
    update_expired_claims = updateExpiredClaims(bitcoin_block_height, confirmation_blocks, bitland_block_height)
    
    #update claims that were invalidated by utxo owner moving the parcel
    update_invalidated_claims = updateInvalidatedClaims(bitland_block_height)
    
    #update claims where miner fee/transfer fee was successful and invalidate old ones that were beaten
    update_leading_claims = updateLeadingClaims(bitland_block_height, claim_blocks, claim_increase)
    
    #update claims that have won - 52500
    update_successful_claims = updateSuccessfulClaims(bitland_block_height)
    
    return True

