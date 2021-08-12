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
    updateInvalidatedClaims, updateLeadingClaims, updateSuccessfulClaims
    )
from utilities.sqlUtils import executeSql


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
        
        #get the status of the miner fee associated with the utxo - if no miner fee then it returns NO_CONTINGENCY
        miner_fee_status = getContingency(transaction,'miner_fee',bitcoin_block_height,bitland_block,output_parcel_bitcoin_block_height).get('status')
        
        #get status of the transfer fee associated with the utxo - if no transfer fee then it returns NO_CONTINGENCY
        transfer_fee_status = getContingency(transaction,'transfer_fee',bitcoin_block_height,bitland_block,output_parcel_bitcoin_block_height).get('status')
        
        #find claims associated with the UTXO
        outstanding_claims = getUtxoClaim(output_parcel.get('id'), bitland_block)
        
        #get the status of the claim transaction (if it is a claim UTXO)
        claim_status = getClaimStatus(output_parcel.get('id'), bitland_block)
    
    parcel_output = {
        'is_current_utxo': is_current_utxo, 
        'type': type, 
        'miner_fee_status': miner_fee_status, 
        'transfer_fee_status': transfer_fee_status, 
        'outstanding_claims': outstanding_claims, 
        'claim_status': claim_status
    }
    
    return parcel_output


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


################CLAIM CALCULATIONS AND DB OPERATIONS
def updateClaims(bitcoin_block_height, confirmation_blocks, bitland_block_height, claim_blocks, claim_increase):

    #UPDATE rollback function to handle claims table and bitcoin transaction table
    
    #OPEN
    #EXPIRED_CONFIRMED
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
    update_successful_claims = updateSuccessfulClaims(bitland_block_height, claim_blocks)
    
    return True


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
    
    if claim_info.get('status') == 'unidentified':
        claim_status = 'NO_CLAIM'
    
    elif claim_info.get('leading_claim') == 'false':
        claim_status = 'SUPERCEDED_CLAIM'
    
    elif claim_info.get('invalidated_claim') == 'true':
        claim_status = 'INVALIDATED_CLAIM'
        
    elif (claim_info.get('leading_claim') == True and claim_info.get('invalidated_claim') == False):
        claim_expiration_block = claim_info.get('claim_block_height') + claim_blocks
        if bitland_block < claim_expiration_block:
            claim_status = 'OUTSTANDING_CLAIM'
        else:
            claim_status = 'SUCCESSFUL_CLAIM'
    
    else:
        claim_status = 'error'
    
    return claim_status


#UPDATE this needs to have logic around claims not having paid the miner fee yet
def getUtxoClaim(utxo_id, bitland_block):

    claim_info = getClaim(claimed_output_parcel_id = utxo_id)
    
    if claim_info.get('status') == 'no claim found':
        claim_status = 'NO_CLAIM'
        
    elif claim_info.get('invalidated_claim') == True:
        claim_status = 'INVALIDATED_CLAIM'
        
    elif (claim_info.get('leading_claim') == True and claim_info.get('invalidated_claim') == False):
        claim_expiration_block = claim_info.get('claim_block_height') + claim_blocks
        if bitland_block < claim_expiration_block:
            claim_status = 'OUTSTANDING_CLAIM'
        else:
            claim_status = 'SUCCESSFUL_CLAIM'    
            
    else: 
        claim_status = 'ERROR'
    
    return claim_status


'''
def getContingencyOld(transaction_hash,type,bitcoin_height,bitland_height,utxo_bitcoin_block_height):
    
    #check DB
    db_contingency = getContingencyStatusDb(transaction_hash=transaction_hash, type=type)
    
    if db_contingency.get('status') == 'contingency identified' :        
        if db_contingency.get('recorded_status') in ['EXPIRED_CONFIRMED', 'VALIDATED_CONFIRMED']:
            return {
                'status': db_contingency.get('recorded_status'),
                'validation_bitcoin_height': db_contingency.get('validation_bitcoin_height')
                }
    
        else:
            calculate_contingency = calculateContingencyStatus(transaction_hash,type,bitcoin_height)
            transaction_id = getTransaction(transaction_hash).get('id')
            
            status = calculate_contingency.get('status')
            bitcoin_txid = calculate_contingency.get('bitcoin_txid')
            validation_bitcoin_height = calculate_contingency.get('bitcoin_block_height') or 0
            
            if db_contingency.get('recorded_status') == 'no recorded status':
                addContingencyStatusDb(transaction_id=transaction_id, type=type, recorded_status_bitcoin_block_height=bitcoin_height, recorded_status_bitland_block_height=bitland_height, status=status, bitcoin_transaction_id=bitcoin_txid, validation_bitcoin_height=validation_bitcoin_height)
            else:
                updateContingencyStatusDb(transaction_id=transaction_id, type=type, recorded_status_bitcoin_block_height=bitcoin_height, recorded_status_bitland_block_height=bitland_height, status=status, bitcoin_transaction_id=bitcoin_txid, validation_bitcoin_height=validation_bitcoin_height)
            
            return {
                'status': status,
                'validation_bitcoin_height': validation_bitcoin_height
            }
    
    elif db_contingency.get('status') == 'no contingency found' : 
        return {
            'status': 'NO_CONTINGENCY',
            'validation_bitcoin_height': utxo_bitcoin_block_height
            }
        
    return None


def calculateContingencyStatus(transaction_hash,type,bitcoin_height):
    
    transaction = getTransaction(transaction_hash=transaction_hash)
    
    if type == 'miner_fee':
        bitcoin_address = hexlify(transaction.get('miner_bitcoin_address').encode('utf-8')).decode('utf-8')
        fee_sats = transaction.get('miner_fee_sats')
        expiration_block = transaction.get('bitcoin_block_height') + transaction.get('miner_fee_blocks')
        expiration_confirmed_block = expiration_block + contingency_validation_blocks
    
    elif type == 'transfer_fee':
        bitcoin_address = hexlify(transaction.get('transfer_fee_address').encode('utf-8')).decode('utf-8')
        fee_sats = transaction.get('transfer_fee_sats')
        expiration_block = transaction.get('bitcoin_block_height') + transaction.get('transfer_fee_blocks')
        expiration_confirmed_block = expiration_block + contingency_validation_blocks

    bitcoin_address_search = getLowestBlockAddressFee(bitcoin_address,fee_sats)

    if bitcoin_address_search.get('status') == 'fee address not found':
        if bitcoin_height > expiration_block:
            status = 'EXPIRED'
        else:
            status = 'OPEN'
            
    elif bitcoin_address_search.get('status') == 'identified fee address':
        if bitcoin_address_search.get('block_height') > expiration_block:
            status = 'EXPIRED'
        elif bitcoin_address_search.get('block_height') <= expiration_block:
            status = 'VALIDATED'
    
    if status == 'EXPIRED':
        if bitcoin_height > expiration_confirmed_block:
            status = 'EXPIRED_CONFIRMED'
        elif bitcoin_height > expiration_block:
            status = 'EXPIRED_UNCONFIRMED'
    
    if status == 'VALIDATED':
        if bitcoin_address_search.get('block_height') + contingency_validation_blocks > bitcoin_height:
            status = 'VALIDATED_UNCONFIRMED'
        else:
            status = 'VALIDATED_CONFIRMED'
    
    output = {
        'status': status,
        'bitcoin_txid': bitcoin_address_search.get('txid') or '',
        'bitcoin_block_height': bitcoin_address_search.get('block_height') 
        }
    
    return output


def addContingencyStatusDb(transaction_id=0, type='', recorded_status_bitcoin_block_height=0, recorded_status_bitland_block_height=0, status='', bitcoin_transaction_id='', validation_bitcoin_height=0):
    
    transaction_id = str(transaction_id)
    recorded_status_bitcoin_block_height = str(recorded_status_bitcoin_block_height)
    recorded_status_bitland_block_height = str(recorded_status_bitland_block_height) 
    validation_bitcoin_height = str(validation_bitcoin_height) 
    
    query = ("insert into bitland.contingency_status values  " +
            "(" + transaction_id + "," +
            "'" + type + "'," + 
            recorded_status_bitcoin_block_height + "," +  
            recorded_status_bitland_block_height + "," +  
            "'" + status + "'," +  
            "'" + bitcoin_transaction_id + "'," +  
            validation_bitcoin_height + ") " +
            "RETURNING transaction_id;"
            )

    claim_id = executeSql(query)
    
    return claim_id


def updateContingencyStatusDb(transaction_id=0, type='', recorded_status_bitcoin_block_height=0, recorded_status_bitland_block_height=0, status='', bitcoin_transaction_id='', validation_bitcoin_height=0):
    
    transaction_id = str(transaction_id)
    recorded_status_bitcoin_block_height = str(recorded_status_bitcoin_block_height)
    recorded_status_bitland_block_height = str(recorded_status_bitland_block_height) 
    validation_bitcoin_height = str(validation_bitcoin_height) 
    
    query = ("update bitland.contingency_status set recorded_status_bitcoin_block_height = " + recorded_status_bitcoin_block_height + ", recorded_status_bitland_block_height = " + recorded_status_bitland_block_height + ", status = '" + status + "', bitcoin_transaction_id = '" + bitcoin_transaction_id + "', validation_bitcoin_height = " + validation_bitcoin_height +  " where transaction_id = " + transaction_id + "and type = '" + type + "' RETURNING transaction_id")
    update = executeSql(query)[0]
    
    return update
    
    
def getLowestBlockAddressFee(address_hex, fee):
    
    address_utf8 = unhexlify(address_hex).decode('utf-8')
    address_search_url_sub = address_search_url.replace(':address', address_utf8)
    
    address_info = requests.get(address_search_url_sub).json()
    
    address_count = len(address_info)
    
    transaction = {
        'status':'fee address not found'
        }
    
    transactions = []
    
    #UPDATE to go through next pages if more than 25 occurrences
    for i in range(0, address_count):
        txid = address_info[i].get('txid')
        block_height = address_info[i].get('status').get('block_height')
        vout = address_info[i].get('vout')
        vout_len = len(vout)
        
        for j in range(0, vout_len):     
            vout_address = vout[j].get('scriptpubkey_address')
            value = vout[j].get('value')
            if vout_address == address_utf8 and value == fee:
                transactions.append([txid, block_height, j, vout_address, value])
    
    matched_transactions = len(transactions)
    print(matched_transactions)
    
    if matched_transactions > 0:
        lowest_block_height = 0
    
        for i in range(0, matched_transactions):
            if lowest_block_height == 0:
                transaction = transactions[i]
            else:
                if transactions[i][1] < transaction[1]:
                    transaction = transactions[i]
                    lowest_block_height = transactions[i][1]
    
        transaction = {
            'status':'identified fee address',
            'txid': transaction[0],
            'block_height': transaction[1],
            'address': transaction[3],
            'value': transaction[4]
            }

    return transaction

'''


if __name__ == '__main__':

    address = 'bc1q2vla02kvsslyfdg3tpdwt6whmfrsdkc7d0kkws'
    address_hex = hexlify(address.encode('utf-8')).decode('utf-8')
    
    #print(getContingency('a8788b7873e8c5671d62c2f3936b34ec3207bfc68062ea4250e4b10182dd8845','miner_fee',694208,230,693905))
    #print(getUtxoClaim(utxo_id=709, bitland_block=239))
    #print(getClaim(claimed_output_parcel_id = 709))
    #print(utxoCombinedContingencyStatus(556,694208,230))
    
    print(analyzeClaimsForOutput(709,694208,230))
