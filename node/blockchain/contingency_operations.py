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
    getClaim
    )


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
        is_current_utxo = True
        type = output_parcel.get('output_version')
        miner_fee_status = getMinerFeeStatus(output_parcel.get('id'), bitcoin_block_height)
        transfer_fee_status = getTransferFeeStatus(output_parcel.get('id'), bitcoin_block_height)
        outstanding_claims = getUtxoClaim(output_parcel.get('id'), bitland_block)
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


def getMinerFeeStatus(utxo_id, bitcoin_block):

    input_utxo = getUtxo(id=utxo_id)
    input_utxo_version = input_utxo.get('output_version')
    miner_fee_sats = input_utxo.get('miner_fee_sats')
    miner_bitcoin_address = input_utxo.get('miner_bitcoin_address')
    miner_fee_expiration_block = input_utxo.get('bitcoin_block_height') + input_utxo.get('miner_fee_blocks')
    miner_fee_status_db = input_utxo.get('miner_fee_status')
    miner_fee_status_block_height_db = input_utxo.get('miner_fee_status_block_height')
    
    #determine if no fee
    if miner_fee_sats == 0:
        miner_fee_status = 'NO_FEE'
    
    else: 
        #look in database
        if miner_fee_status_db != None:
            miner_fee_status = miner_fee_status_db
            status_block = miner_fee_status_block_height_db
        
        #if not found in database, look it up from blockchain, don't try to save it in the db at this step
        else:
            calc_miner_fee_status = calculateMinerFeeStatus(utxo_id, bitcoin_block)
            miner_fee_status = calc_miner_fee_status.get('status')
            status_block = calc_miner_fee_status.get('bitcoin_block_height')
            
        if miner_fee_status == 'VALIDATED':
            if status_block + contingency_validation_blocks <= bitcoin_block:
                miner_fee_status = 'VALIDATED_CONFIRMED'
            else:
                miner_fee_status = 'VALIDATED_UNCONFIRMED'
                
        elif miner_fee_status == 'EXPIRED':
            if miner_fee_expiration_block + contingency_validation_blocks <= bitcoin_block:
                miner_fee_status = 'EXPIRED_CONFIRMED'
            else:
                miner_fee_status = 'EXPIRED_UNCONFIRMED'
        
        elif miner_fee_expiration_block > bitcoin_block:
            miner_fee_status = 'OPEN'
            
        else: 
            miner_fee_status = 'error'

    return miner_fee_status


def getTransferFeeStatus(utxo_id, bitcoin_block):

    input_utxo = getUtxo(id=utxo_id)
    input_utxo_version = input_utxo.get('output_version')
    transfer_fee_sats = input_utxo.get('transfer_fee_sats')
    failed_transfer_fee_address = input_utxo.get('transfer_fee_failover_address')
    transfer_fee_expiration_block = input_utxo.get('bitcoin_block_height') + input_utxo.get('transfer_fee_blocks')
    transfer_fee_status_db = input_utxo.get('transfer_fee_status')
    transfer_fee_status_block_height_db = input_utxo.get('transfer_fee_status_block_height')

    #determine if no fee
    if transfer_fee_sats == 0:
        transfer_fee_status = 'NO_FEE'    

    else: 
        #look in database
        if transfer_fee_status_db != None:
            transfer_fee_status = transfer_fee_status_db
            status_block = transfer_fee_status_block_height_db
        
        #UPDATE
        #if not found in database, look it up from blockchain, don't try to save it in the db at this step
        else:
            calc_transfer_fee_status = calculateTransferFeeStatus(bitcoin_block=bitcoin_block, utxo_id=utxo_id)
            transfer_fee_status = calc_transfer_fee_status.get('status')
            status_block = calc_transfer_fee_status.get('bitcoin_block_height')
            
        if transfer_fee_status == 'VALIDATED':
            if status_block + contingency_validation_blocks <= bitcoin_block:
                transfer_fee_status = 'VALIDATED_CONFIRMED'
            else:
                transfer_fee_status = 'VALIDATED_UNCONFIRMED'
                
        elif transfer_fee_status == 'EXPIRED':
            if transfer_fee_expiration_block + contingency_validation_blocks <= bitcoin_block:
                transfer_fee_status = 'EXPIRED_CONFIRMED'
            else:
                transfer_fee_status = 'EXPIRED_UNCONFIRMED'
        
        elif transfer_fee_expiration_block > bitcoin_block:
            transfer_fee_status = 'OPEN'
            
        else: 
            transfer_fee_status = 'error'

    return transfer_fee_status


def getClaimStatus(utxo_id, bitland_block):

    claim_info = getClaim(claim_action_output_parcel_id = utxo_id)
    
    if claim_info.get('status') == 'unidentified':
        claim_status = 'NO_CLAIM'
    
    elif claim_info.get('leading_claim') == 'false':
        claim_status = 'SUPERCEDED_CLAIM'
    
    elif claim_info.get('invalidated_claim') == 'true':
        claim_status = 'INVALIDATED_CLAIM'
        
    elif (claim_info.get('leading_claim') == 'true' and claim_info.get('invalidated_claim') == 'false'):
        claim_expiration_block = claim_info.get('claim_block_height') + claim_blocks
        if bitland_block < claim_expiration_block:
            claim_status = 'OUTSTANDING_CLAIM'
        else:
            claim_status = 'SUCCESSFUL_CLAIM'
    
    else:
        claim_status = 'error'
    
    return claim_status


def getUtxoClaim(utxo_id, bitland_block):

    claim_info = getClaim(claimed_output_parcel_id = utxo_id)
    
    if claim_info.get('status') == 'no claim found':
        claim_status = 'NO_CLAIM'
        
    elif claim_info.get('invalidated_claim') == 'true':
        claim_status = 'INVALIDATED_CLAIM'
        
    elif (claim_info.get('leading_claim') == 'true' and claim_info.get('invalidated_claim') == 'false'):
        claim_expiration_block = claim_info.get('claim_block_height') + claim_blocks
        if bitland_block < claim_expiration_block:
            claim_status = 'OUTSTANDING_CLAIM'
        else:
            claim_status = 'SUCCESSFUL_CLAIM'    
    
    return claim_status


def calculateMinerFeeStatus(utxo_id, bitcoin_block):
    
    input_utxo = getUtxo(id=utxo_id)
    miner_fee_sats = input_utxo.get('miner_fee_sats')
    miner_bitcoin_address = input_utxo.get('miner_bitcoin_address')
    miner_fee_expiration_block = input_utxo.get('bitcoin_block_height') + input_utxo.get('miner_fee_blocks')
    
    miner_fee = getLowestBlockAddressFee(hexlify(miner_bitcoin_address.encode('utf-8')), miner_fee_sats)
    miner_fee_status = miner_fee[0]
    
    status = {'status':'ERROR','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
    
    if miner_fee_status == 'fee address not found':
        if bitcoin_block > miner_fee_expiration_block:
            status = {'status':'EXPIRED','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
        else:
            status = {'status':'OPEN','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
            
    elif miner_fee_status == 'identified fee address':
        if miner_fee[2] <= miner_fee_expiration_block:
            status = {'status':'VALIDATED','txid':miner_fee[1],'bitcoin_block_height':miner_fee[2],'transaction_number':miner_fee[3],'address':miner_fee[4],'value':miner_fee[5]}
        else:
            status = {'status':'EXPIRED','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
    
    else: 
        status = {'status':'ERROR','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
    
    return status


#UPDATE combine with one above
def calculateMinerFeeStatusTransaction(transaction_id, bitcoin_block):
    
    print(transaction_id)
    
    transaction_info = getTransaction(id = transaction_id)
    miner_fee_sats = transaction_info.get('miner_fee_sats')
    miner_bitcoin_address = transaction_info.get('miner_bitcoin_address')
    miner_fee_expiration_block = transaction_info.get('bitcoin_block_height') + transaction_info.get('miner_fee_blocks')
    
    miner_fee = getLowestBlockAddressFee(miner_bitcoin_address, miner_fee_sats)
    miner_fee_status = miner_fee[0]
    
    if miner_fee_status == 'fee address not found':
        if bitcoin_block > miner_fee_expiration_block:
            status = ['EXPIRED','',0,0,'',0]
        else:
            status = ['OPEN','',0,0,'',0]
            
    elif miner_fee_status == 'identified fee address':
        if miner_fee[2] <= miner_fee_expiration_block:
            status = ['VALIDATED',miner_fee[1],miner_fee[2],miner_fee[3],miner_fee[4],miner_fee[5]]
        else:
            status = ['EXPIRED','',0,0,'',0]
    
    else: 
        status = ['ERROR','',0,0,'',0]
    
    return status


#UPDATE
def calculateTransferFeeStatus(bitcoin_block, utxo_id=0, transaction_id=0):

    if utxo_id != 0:
        input_utxo = getUtxo(id=utxo_id)
        transfer_fee_sats = input_utxo.get('transfer_fee_sats')
        transfer_fee_bitcoin_address = input_utxo.get('transfer_fee_address')
        transfer_fee_expiration_block = input_utxo.get('bitcoin_block_height') + input_utxo.get('transfer_fee_blocks')
    
    else:
        transaction_info = getTransaction(id = transaction_id)
        transfer_fee_sats = transaction_info.get('transfer_fee_sats')
        transfer_fee_bitcoin_address = transaction_info.get('transfer_fee_address')
        transfer_fee_expiration_block = transaction_info.get('bitcoin_block_height') + transaction_info.get('transfer_fee_blocks')
    
    transfer_fee = getLowestBlockAddressFee(transfer_fee_bitcoin_address, transfer_fee_sats)
    transfer_fee_status = transfer_fee[0]
    
    status = {'status':'ERROR','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
    
    if transfer_fee_status == 'fee address not found':
        if bitcoin_block > transfer_fee_expiration_block:
            status = {'status':'EXPIRED','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
        else:
            status = {'status':'OPEN','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
            
    elif transfer_fee_status == 'identified fee address':
        if transfer_fee[2] <= transfer_fee_expiration_block:
            status = {'status':'VALIDATED','txid':transfer_fee[1],'bitcoin_block_height':transfer_fee[2],'transaction_number':transfer_fee[3],'address':transfer_fee[4],'value':transfer_fee[5]}
        else:
            status = {'status':'EXPIRED','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
    
    else: 
        status = {'status':'ERROR','txid':'','bitcoin_block_height':0,'transaction_number':0,'address':'','value':0}
    
    return status


def getLowestBlockAddressFee(address_hex, fee):
    
    address_utf8 = unhexlify(address_hex).decode('utf-8')
    address_search_url_sub = address_search_url.replace(':address', address_utf8)
    
    address_info = requests.get(address_search_url_sub).json()
    
    address_count = len(address_info)
    
    transaction = ['fee address not found']
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
    
        transaction.insert(0, 'identified fee address')

    return transaction


#UPDATE
def getUtxoPubKey(utxo_id, pub_key_input_type):
    
    return 'abc'


if __name__ == '__main__':

    address = '31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668'
    print(unhexlify(address).decode('utf-8'))
    
    address_str = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
    address_hex_bytes = hexlify(address_str.encode('utf-8'))
    print(address_hex_bytes)
    print(len(address_hex_bytes))
    print(unhexlify(address_hex_bytes))

    utxo_id = 21
    transaction = 'b0bcaa0b93e0802533596449a9efa39f7137895c51baba2fa3eefe38cab8fff6'
    vout = 1
    bitcoin_block = 700000
    bitland_block = 4
    print(inspectParcel(transaction, vout, bitcoin_block, bitland_block))