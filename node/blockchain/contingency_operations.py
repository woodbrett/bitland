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
from utilities.sqlUtils import executeSql


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
        
        '''
        #get the status of the miner fee associated with the utxo - if no miner fee then it returns NO_CONTINGENCY
        miner_fee_status = getContingency(transaction,'miner_fee',bitcoin_block_height,bitland_block,output_parcel_bitcoin_block_height).get('status')
        
        #get status of the transfer fee associated with the utxo - if no transfer fee then it returns NO_CONTINGENCY
        transfer_fee_status = getContingency(transaction,'transfer_fee',bitcoin_block_height,bitland_block,output_parcel_bitcoin_block_height).get('status')
        
        #find claims associated with the UTXO
        outstanding_claims = getUtxoClaim(output_parcel.get('id'), bitland_block)
        
        #get the status of the claim transaction (if it is a claim UTXO)
        claim_status = getClaimStatus(output_parcel.get('id'), bitland_block)
        '''
        
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
    add_new_contingencies = addNewContingenciesDb(bitcoin_block_height)
    
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
    
    #update claims where miner fee/transfer fee expired
    update_expired_claims = updateExpiredClaims(bitcoin_block_height, confirmation_blocks, bitland_block_height)
    
    #update claims that were invalidated by utxo owner moving the parcel
    update_invalidated_claims = updateInvalidatedClaims(bitland_block_height)
    
    #update claims where miner fee/transfer fee was successful and invalidate old ones that were beaten
    update_leading_claims = updateLeadingClaims(bitland_block_height, claim_blocks, claim_increase)
    
    #update claims that have won - 52500
    update_successful_claims = updateSuccessfulClaims(bitland_block_height)
    
    return True


'''
#UPDATE might not need
def utxoCombinedContingencyStatus(utxo_id, bitcoin_height, bitland_height):

    output_parcel = getUtxo(id=utxo_id)
    transaction_hash = output_parcel.get('transaction_hash')
    utxo_bitcoin_block_height = output_parcel.get('bitcoin_block_height')
    miner_fee_sats = output_parcel.get('miner_fee_sats')
    
    miner_fee_status = getContingency(transaction_hash,'miner_fee',bitcoin_height,bitland_height,utxo_bitcoin_block_height)
    transfer_fee_status = getContingency(transaction_hash,'transfer_fee',bitcoin_height,bitland_height,utxo_bitcoin_block_height)
    
    if miner_fee_status.get('status') == 'EXPIRED_CONFIRMED' or transfer_fee_status.get('status') == 'EXPIRED_CONFIRMED':
        return {
            'status': 'EXPIRED_CONFIRMED'
        }
    
    if miner_fee_status.get('status') == 'EXPIRED_UNCONFIRMED' or transfer_fee_status.get('status') == 'EXPIRED_UNCONFIRMED':
        return {
            'status': 'EXPIRED_UNCONFIRMED'
        }    
        
    if miner_fee_status.get('status') == 'OPEN' or transfer_fee_status.get('status') == 'OPEN':
        return {
            'status': 'OPEN'
        }   
    
    if miner_fee_status.get('status') == 'VALIDATED_UNCONFIRMED' or transfer_fee_status.get('status') == 'VALIDATED_UNCONFIRMED':
        max_block_height = max( miner_fee_status.get('validation_bitcoin_height'), transfer_fee_status.get('validation_bitcoin_height'))
        return {
            'status': 'VALIDATED_UNCONFIRMED',
            'bitcoin_block_height': max_block_height,
            'miner_fee_sats': miner_fee_sats
        }    
        
    if miner_fee_status.get('status') == 'VALIDATED_CONFIRMED' and transfer_fee_status.get('status') == 'VALIDATED_CONFIRMED':
        max_block_height = max( miner_fee_status.get('validation_bitcoin_height'), transfer_fee_status.get('validation_bitcoin_height'))
        return {
            'status': 'VALIDATED_CONFIRMED',
            'bitcoin_block_height': max_block_height,
            'miner_fee_sats': miner_fee_sats
        }    

    return None




################CONTINGENCY CALCULATIONS AND DB OPERATIONS
def getContingency(transaction_hash,type,bitcoin_height,bitland_height,utxo_bitcoin_block_height):
    
    #check DB
    db_contingency = getContingencyStatusDb(transaction_hash=transaction_hash, type=type)
    
    if db_contingency.get('status') == 'contingency identified' : 
        
        expiration_block = db_contingency.get('bitcoin_expiration_height')
        expiration_confirmed_block = expiration_block + contingency_validation_blocks
        validation_bitcoin_block_height = db_contingency.get('validation_bitcoin_block_height')
        
        if validation_bitcoin_block_height == None:
            if bitcoin_height > expiration_confirmed_block:
                status = 'EXPIRED_CONFIRMED'
            elif bitcoin_height > expiration_block:
                status = 'EXPIRED_UNCONFIRMED'
            elif bitcoin_height <= expiration_block:
                status = 'OPEN'
            
        elif validation_bitcoin_block_height != None:
            if validation_bitcoin_block_height > expiration_block:
                if bitcoin_height > expiration_confirmed_block:
                    status = 'EXPIRED_CONFIRMED'
                elif bitcoin_height > expiration_block:
                    status = 'EXPIRED_UNCONFIRMED'
            elif validation_bitcoin_block_height <= expiration_block:
                if bitcoin_height > expiration_confirmed_block:
                    status = 'VALIDATED_CONFIRMED'
                elif bitcoin_height > expiration_block:
                    status = 'VALIDATED_UNCONFIRMED'

        return {
            'status': status,
            'validation_bitcoin_height': validation_bitcoin_block_height
            }
        
    elif db_contingency.get('status') == 'no contingency found' : 
        return {
            'status': 'NO_CONTINGENCY',
            'validation_bitcoin_height': utxo_bitcoin_block_height
            }
        
    return None



def findClaimsForOutput(output_id):
    
    claims = getClaims(claimed_output_parcel_id = output_id)
    
    return claims


def analyzeClaimsForOutput(output_id, bitcoin_height, bitland_height):
    
    claims = findClaimsForOutput(output_id)
    claims_array = []
    
    for i in range(0,len(claims)):
        claim_action_output_parcel_id = claims[i].get('claim_action_output_parcel_id')
        claim_contingency_status = utxoCombinedContingencyStatus(claim_action_output_parcel_id, bitcoin_height, bitland_height)
        claim_status = claim_contingency_status.get('status')
        claim_validation_block_height = claim_contingency_status.get('bitcoin_block_height')
        miner_fee_sats = claims[i].get('claim_fee_sats')
        claims_array.append([claim_action_output_parcel_id,claim_status,claim_validation_block_height,miner_fee_sats])
    
    return claims_array


def getClaimStatus(utxo_id, bitland_block):

    claim_info = getClaim(claim_action_output_parcel_id = utxo_id)
    
    claim_status = claim_info.get('claim_status') 
    claim_end_block = claim_info.get('claim_end_block') 
    
    if claim_info.get('status') == 'unidentified':
        claim_status = 'NO_CLAIM'
    
    return claim_status


#UPDATE this needs to have logic around claims not having paid the miner fee yet
def getUtxoClaim(utxo_id, bitland_block):

    utxo_info = getUtxo(id=utxo_id) 
    claim_status_utxo = utxo_info.get('claim_status')
    claim_end_block = utxo_info.get('claim_end_block')
    
    if claim_status_utxo == None:
        claim_status = 'UNCLAIMED'
        
    elif claim_status_utxo == 'SUCCESSFUL':
        claim_status = claim_status_utxo 
    
    else:
        claim_status = 'ERROR'
        
    return claim_status
'''

if __name__ == '__main__':

    address = 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws'
    address_hex = hexlify(address.encode('utf-8')).decode('utf-8')
    
    #print(getContingency('a8788b7873e8c5671d62c2f3936b34ec3207bfc68062ea4250e4b10182dd8845','miner_fee',694208,230,693905))
    #print(getUtxoClaim(utxo_id=709, bitland_block=239))
    #print(getClaim(claimed_output_parcel_id = 709))
    #print(utxoCombinedContingencyStatus(556,694208,230))
    
    #print(analyzeClaimsForOutput(709,694208,230))
    
    print(getClaimStatus(882, 40))
    print(getUtxoClaim(862, 40))
