'''
Created on Dec 23, 2020

@author: brett_wood
'''

from node.blockchain.transaction_serialization import deserialize_transaction
from utilities.serialization import deserialize_text
from utilities.sqlUtils import executeSql
import psycopg2
from utilities.config import config
from binascii import unhexlify, hexlify
import ecdsa
from node.blockchain.queries import *
from collections import namedtuple
from node.blockchain.global_variables import *
from system_variables import address_search_url
import requests
from utilities.bitcoin_requests import *
from node.blockchain.contingency_operations import *

#input version 1 - standard spend (which could be a scuessful collateral)
#input version 2 - spending as collateral
#input version 3 - make claim
#input version 4 - spend failed transfer
#input version 5 - spend successful claim

#input version 1 - standard 
#input version 2 - spending as collateral
#input version 3 - make claim
#input version 4 - n/a
#input version 5 - n/a

def validateTransaction(transaction):
    
    transaction = deserialize_transaction(transaction)
    transaction_state = []
    
    transaction_type = transaction[0]
    transaction_type_int = int.from_bytes(transaction_type, byteorder='big')
    
    if (transaction_type_int == 1):
      transaction_state = validateTransaction1(transaction)
    
    elif (transaction_type_int == 2):
      transaction_state = validateTransaction2(transaction)
      
    else:
      transaction_state = [False, 'invalid transaction type']
    
    return (transaction_state)

    
def validateTransaction1(transaction):
    #landbase transaction
    
    inputs = transaction[1]
    contingencies = transaction[3]
    output_length = len(transaction[2])
    output_version = int.from_bytes(transaction[2][0][0],'big')
    planet_id = int.from_bytes(transaction[2][0][1],'big')
    shape = transaction[2][0][2].decode('utf-8')
    miner_fee_sats = int.from_bytes(transaction[3][0] ,'big')
    miner_fee_blocks = int.from_bytes(transaction[3][1] ,'big')
    transfer_fee_sats = int.from_bytes(transaction[3][2] ,'big')
    transfer_fee_blocks = int.from_bytes(transaction[3][3] ,'big')
    transfer_fee_address = transaction[3][4].decode('utf-8')
    
    valid_transaction = True
    failure_reason = ''
    
    #check no inputs
    if (valid_transaction == True):
        valid_transaction = inputs == []
        if(valid_transaction == False):
            failure_reason = '>0 inputs in landbase transaction'
    
    #check only 1 output
    if (valid_transaction == True):
        valid_transaction = output_length == 1
        if(valid_transaction == False):
            failure_reason = 'outputs <> 1 in landbase transaction'
            
    #check output is version 4
    if (valid_transaction == True):
        valid_transaction = output_version == 0
        if(valid_transaction == False):
            failure_reason = 'wrong output version, needs to be 0 for landbase'
        
    #check only planet id 1
    if (valid_transaction == True):
        valid_transaction = planet_id == 1
        if(valid_transaction == False):
            failure_reason = 'planet_id <> 1'
    
    #check that its a valid reward
    if (valid_transaction == True):
        query_valid_reward = ("select count(*) "
                              + "from bitland.landbase_enum "
                              + "where valid_claim = true "
                              + "and st_equals(geom, st_geomfromtext('"
                              + shape
                              + "',4326))")

        try:
            count = executeSql(query_valid_reward)[0]
            valid_transaction = count == 1
            
            if(valid_transaction == False):
                failure_reason = 'invalid landbase reward geography'
        
        except Exception as error:
            valid_transaction = False
            failure_reason = 'invalid landbase reward - ' + str(error)
    
    #check that all contingencies are 0
    if (valid_transaction == True):
        valid_transaction = (
            miner_fee_sats == 0 
            and miner_fee_blocks == 0 
            and transfer_fee_sats == 0 
            and transfer_fee_blocks == 0 
            and transfer_fee_address == '' )
        if(valid_transaction == False):
            failure_reason = 'landbase contingency violation'
            
    return valid_transaction, failure_reason


def validateTransaction2(transaction, bitcoin_block):
    #standard transaction
    inputs = transaction[1]
    outputs = transaction[2]
    miner_fee_sats = int.from_bytes(transaction[2][0],'big')
    
    try:
        #validate inputs
        valid_inputs = validateTransactionInputs(inputs,miner_fee_sats)
        if valid_inputs[0] == False:
            raise Exception(valid_inputs[0], valid_inputs[1])
       
        #validate input claims match output claims
        valid_outputs = validateInputOutputClaims(inputs, outputs)
        if valid_outputs[0] == False:
            raise Exception(valid_outputs[0], valid_outputs[1])
        
        #validate shapes
        valid_shapes = validateShapes(inputs, outputs)
        if valid_shapes[0] == False:
            raise Exception(valid_shapes[0], valid_shapes[1])
        
        #UPDATE logic to check for planets when it expands beyond 1
        valid_outputs = validateTransactionOutputs(outputs)
        if valid_outputs[0] == False:
            raise Exception(valid_outputs[0], valid_outputs[1])
        
        #UPDATE validate contingency values
        #miner fee >= 0
        #miner fee blocks <=12096
        #transfer fee >= 0
        #transfer fee blocks <=12096
            
    except Exception as inst: 
        transaction_status, reason = inst.args  
        print("transaction status: " + str(transaction_status))
        print("reason: " + str(reason))
    
    return transaction_status, reason


def validateTransactionOutputs(outputs):

    valid_output = True
    failure_reason = ''

    output_length = len(outputs)
    for i in range(0, output_length):
        
        planet_id = int.from_bytes(outputs[i][1],'big')
        #currently only output validation is to check that planet id = 1
        valid_output = planet_id == 1

        if valid_output == False:
            failure_reason = 'planet id <> 1'
            break
        
    return valid_output, failure_reason


def validateTransactionInputs(inputs, bitcoin_block, miner_fee_sats):
    
    valid_input = True
    failure_reason = ''

    input_length = len(inputs)
    for i in range(0, input_length):

        validate_input = validateTransactionInput(inputs[i], miner_fee_sats)
        valid_input = validate_input[0]
        failure_reason = validate_input[1]

        if valid_input == False:
            break
        
    return valid_input, failure_reason


#claims only support a single input and ouptut claim per transaction
def validateInputOutputClaims(inputs, outputs):
    
    valid_input = True
    failure_reason = ''
    input_claim_count = 0
    output_claim_count = 0

    input_length = len(inputs)
    for i in range(0, input_length):
        input_version = int.from_bytes(inputs[i][0],'big')
        transaction_hash = hexlify(inputs[i][1]).decode('utf-8')
        transaction_vout = int.from_bytes(inputs[i][2],'big')
        if input_version == 3:
            input_claim_count = input_claim_count + 1
            output_parcel = getOutputParcelByTransactionVout(transaction_hash, transaction_vout)
            input_shape_str = output_parcel[1]
            input_claim_geom = "st_geomfromtext('" + input_shape_str + "',4326)"
    
    output_length = len(outputs)
    for i in range(0, input_length):
        output_version = int.from_bytes(outputs[i][0],'big')
        if output_version == 3:
            output_claim_count = output_claim_count + 1
            output_shape_str = outputs[i][2].decode('utf-8')
            output_claim_geom = "st_geomfromtext('" + output_shape_str + "',4326)"

    #validate 1 or fewer claim attempt
    if (valid_input == True):
        valid_input = input_claim_count <= 1
        if(valid_input == False):
            failure_reason = 'more than 1 claim'
            
    #validate input and output claim count match
    if (valid_input == True):
        valid_input = output_claim_count == input_claim_count
        if(valid_input == False):
            failure_reason = 'input claim count not matching output claim count'
        
    #validate claim geometries match
    if (valid_input == True and input_claim_count == 1):
        valid_input = queryPolygonEquality(input_claim_geom, output_claim_geom)
        if(valid_input == False):
            failure_reason = 'claim geometries dont match'
    
    return valid_input, failure_reason


def validateShapes(inputs, outputs):
    
    valid_shapes = True
    failure_reason = ''
    
    input_union_shape = getInputUnionShape(inputs)
    output_union_shape = getOutputUnionShape(outputs)[0]
    
    output_union_area = queryUnionPolygonAreaMeters(output_union_shape)
    sum_output_area = getOutputUnionShape(outputs)[1]
    
    #validate input shape matches output transaction shape
    if (valid_shapes == True):
        valid_shapes = queryPolygonEquality(input_union_shape, output_union_shape)
        if(valid_shapes == False):
            failure_reason = 'input polygons not equal to output polygons'

    #validate area of unioned outputs = sum of individual areas
    if (valid_shapes == True):
        valid_shapes = output_union_area == sum_output_area
        if(valid_shapes == False):
            failure_reason = 'sum of individual outputs not equal to unioned output'
    
    return valid_shapes, failure_reason


def getInputUnionShape(inputs):

    input_length = len(inputs)
    inputs_info = []
    input_union_shape = 'st_union(array['
    
    for i in range(0, input_length):
        transaction_hash = hexlify(inputs[i][1]).decode('utf-8')
        transaction_vout = int.from_bytes(inputs[i][2],'big')
        output_parcel = getOutputParcelByTransactionVout(transaction_hash, transaction_vout)
        shape_str = output_parcel[1]
        shape = shape_str.encode('utf-8')
        
        if (i == 0):
            input_union_shape = input_union_shape + "st_geomfromtext('" + shape_str + "',4326)"
        
        else:
            input_union_shape = input_union_shape + ",st_geomfromtext('" + shape_str + "',4326)"
        
    input_union_shape = input_union_shape + "])"
    
    return input_union_shape


def getOutputUnionShape(outputs):
    
    output_length = len(outputs)
    outputs_info = []
    output_union_shape = 'st_union(array['
    sum_output_area = 0
    
    for i in range(0, output_length):
        output_shape = outputs[i][2].decode('utf-8')
        if (i == 0 ):
            output_union_shape = output_union_shape + "st_geomfromtext('" + output_shape + "',4326)"
        
        else:
            output_union_shape = output_union_shape + ",st_geomfromtext('" + output_shape + "',4326)"
        
        output_area = queryPolygonAreaMeters(output_shape)
        sum_output_area = sum_output_area + output_area

    output_union_shape = output_union_shape + "])"
    output_union_area = queryUnionPolygonAreaMeters(output_union_shape)
    
    return output_union_shape, output_union_area


def validateTransactionInput(input, bitcoin_block, miner_fee_sats):
    
    input_version = int.from_bytes(input[0],'big')
    transaction_hash = hexlify(input[1]).decode('utf-8')
    transaction_vout = int.from_bytes(input[2],'big')
    input_signature = input[3]
    print(transaction_hash, transaction_vout)
    input_utxo = getOutputParcelByTransactionVout(transaction_hash, transaction_vout)
    inspected_parcel = inspectParcel(transaction_hash, transaction_vout)
    
    valid_input = True
    failure_reason = ''
    
    #validate it is an outstanding utxo
    if (valid_input == True):
        valid_input = input_utxo != 'no matched utxo'
        if(valid_input == False):
            failure_reason = 'no matched utxo'
    
    if (valid_input == True):

        input_utxo_version = input_utxo.output_version
        input_utxo_id = input_utxo.id
        input_utxo_shape = input_utxo.shape
        input_utxo_pub_key = input_utxo.pub_key
        input_utxo_collateral_pub_key = input_utxo.miner_landbase_address
        input_utxo_failed_transfer_pub_key = input_utxo.transfer_fee_failover_address
    
        #get summary of utxo - what is its transfer fee status, miner fee status
        #UPDATE to pull data from contingency logic
        transfer_fee_status = inspected_parcel.transfer_fee_status
        miner_fee_status = inspected_parcel.miner_fee_status
        claim_status = inspected_parcel.claim_status
        outstanding_claim = inspected_parcel.outstanding_claims

        valid_transfer_fee_types = validContingencyStatusSpendTypes(input_version)[0]
        valid_miner_fee_types = validContingencyStatusSpendTypes(input_version)[1]
        valid_claim_types = validContingencyStatusSpendTypes(input_version)[2]
        valid_outstanding_claim_types = validContingencyStatusSpendTypes(input_version)[3]
        valid_input_utxo_types = validContingencyStatusSpendTypes(input_version)[4]
        
        transfer_fee_status_valid = ((transfer_fee_status in valid_transfer_fee_types) or valid_transfer_fee_types == [])
        miner_fee_status_valid = ((miner_fee_status in valid_miner_fee_types) or valid_transfer_fee_types == [])
        claim_status_valid = ((claim_status in valid_claim_types) or valid_claim_types == [])
        outstanding_claim_valid = ((outstanding_claim in valid_claim_types) or valid_claim_types == [])
        input_utxo_type_valid = ((input_utxo_version in valid_input_utxo_types) or valid_input_utxo_types == [])
        
        valid_input = transfer_fee_status_valid == True 
        if(valid_input == False):
            failure_reason = 'invalid transfer fee status'        
    
        if (valid_input == True):
            valid_input = miner_fee_status_valid == True
            if(valid_input == False):
                failure_reason = 'invalid miner fee status'  
                
        if (valid_input == True):
            valid_input = claim_status_valid == True
            if(valid_input == False):
                failure_reason = 'invalid claim status'  
                
        if (valid_input == True):
            valid_input = outstanding_claim_valid == True
            if(valid_input == False):
                failure_reason = 'invalid claim on utxo'  
                
        if (valid_input == True):
            valid_input = input_utxo_type_valid == True
            if(valid_input == False):
                failure_reason = 'invalid input utxo type for the spend type'  
    
    #check if its valid to make a claim
    if (valid_input == True and input_version == 3):
        utxo_current_claim_sats = input_utxo.claim_fee_sats
        valid_input = validateClaimAttempt(miner_fee_sats, utxo_current_claim_sats)
        if(valid_input == False):
            failure_reason = 'insufficient bid for claim'          
    
    #validate signature, but not for making a claim
    if (valid_input == True and input_version != 3):
        resolved_pub_key = getPublicKeySpendTypes(input_version, input_utxo_pub_key, input_utxo_failed_transfer_pub_key, input_utxo_collateral_pub_key)    
        print(input_version)
        print(resolved_pub_key)        
        valid_input = validateSignature(input_utxo_shape, resolved_pub_key, input_signature)
        if(valid_input == False):
            failure_reason = 'signature failed'  
        
    return valid_input, failure_reason


def getPublicKeySpendTypes(spend_type, utxo_public_key, utxo_transfer_failover_key, miner_public_key):
    
    if spend_type == 1:
        public_key = utxo_public_key
    
    if spend_type == 2:
        public_key = miner_public_key
          
    if spend_type == 3:
        public_key = ''
          
    if spend_type == 4:
        public_key = utxo_transfer_failover_key
          
    if spend_type == 5:
        public_key = utxo_public_key
          
    return public_key
    

def validContingencyStatusSpendTypes(spend_type):
    #NO_FEE - transaction didn't have a transfer fee
    #FEE_PAID_UNCONFIRMED - fee was paid but not through the confirmation period
    #FEE_PAID_CONFIRMED - fee was paid but not through the confirmation period
    #FEE_UNPAID_NOT_EXPIRED - fee not paid, but timing not expired
    #EXPIRED_UNCONFIRMED - fee not paid, timing expired, waiting for block period
    #EXPIRED_CONFIRMED - fee not paid, waiting period complete, parcel is returned to original address

    #NO_CLAIM, OUTSTANDING_CLAIM, SUCCESSFUL_CLAIM

    if spend_type == 1:
        transfer_fee_status = ['NO_FEE', 'FEE_PAID_CONFIRMED']
        miner_fee_status = ['NO_FEE', 'FEE_PAID_CONFIRMED']
        claim_status = []
        outstanding_claim = ['NO_CLAIM', 'INVALIDATED_CLAIM', 'OUTSTANDING_CLAIM']
        input_utxo_type = [0,1,2]
        
    elif spend_type == 2:
        transfer_fee_status = []
        miner_fee_status = ['EXPIRED_CONFIRMED']
        claim_status = []
        outstanding_claim = ['NO_CLAIM', 'INVALIDATED_CLAIM', 'OUTSTANDING_CLAIM']
        input_utxo_type = [2]
        
    elif spend_type == 3:
        transfer_fee_status = ['NO_FEE', 'FEE_PAID_CONFIRMED', 'EXPIRED_CONFIRMED']
        miner_fee_status = ['NO_FEE', 'FEE_PAID_CONFIRMED', 'EXPIRED_CONFIRMED']
        claim_status = []
        outstanding_claim = ['NO_CLAIM', 'INVALIDATED_CLAIM', 'OUTSTANDING_CLAIM']
        input_utxo_type = [0,1,2,3]
        
    elif spend_type == 4:
        transfer_fee_status = ['EXPIRED_CONFIRMED']
        miner_fee_status = []
        claim_status = []
        outstanding_claim = ['NO_CLAIM', 'INVALIDATED_CLAIM', 'OUTSTANDING_CLAIM']
        input_utxo_type = [0,1,2]
    
    elif spend_type == 5:
        transfer_fee_status = []
        miner_fee_status = ['NO_FEE', 'FEE_PAID_CONFIRMED']
        claim_status = ['SUCCESSFUL_CLAIM']
        outstanding_claim = ['NO_CLAIM', 'INVALIDATED_CLAIM', 'OUTSTANDING_CLAIM']
        input_utxo_type = [3]
    
    else:
        transfer_fee_status = 'error'
        miner_fee_status = 'error'
        claim_status = 'error'

    return transfer_fee_status, miner_fee_status


def validateClaimAttempt(miner_fee_sats, utxo_current_claim_sats):
    
    #claim must be larger than prior claims by 50% (global variable)
    valid_claim_increase = (miner_fee_sats / utxo_current_claim_sats - 1) > claim_required_percentage_increase
    return valid_claim_increase    


def validateSignature(message, public_key, signature):
    
    public_key_encoded = ecdsa.VerifyingKey.from_string(public_key,curve=ecdsa.SECP256k1)
    
    try:
        valid_signature = public_key_encoded.verify(signature, message)
    
    except Exception as error:
        print(str(error))
        valid_signature = False
    
    return valid_signature


if __name__ == '__main__':

    transaction = '00020101b0bcaa0b93e0802533596449a9efa39f7137895c51baba2fa3eefe38cab8fff60040718458a4d630315618b7e311399c5d58fe9ab3474548023821f05975533b354eb7bc394aba99982281cac0a5984699b36feec3dd3c8394480553a925765d6985020101002c504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c30203930292940879dfac7e96660b71f93abdfbd09a8f15d056b3b6149aab233381150b42088c5d03cff0d51178990d08c1d94924abdfdd234837f3b370a435e2b631e33d51edc02010030504f4c59474f4e28282d39302038392e37343637342c2d39302039302c302039302c2d39302038392e37343637342929401bf9fd16296aeda8f680a86ce5505fb52239d14109c9c84e9d84a5be403c9e727144a8b41f1f6cfe6ad2d85268a934c37dd85b895c0f8082bc6ee3a2b7613a4500000000271007d000000007a12001902a626331716571723335646c723266616d6870797738763939767972707834376d67707378726c67786378'
    transaction_bytes = unhexlify(transaction)
    deserialized_transaction = deserialize_transaction(transaction_bytes)
    print(deserialized_transaction[3][0])
    input = deserialize_transaction(transaction_bytes)[1][0]
    print(input)
    
    #print(getUtxoTransferFeeStatus(6, 700000))
    print(validateTransactionInput(input, 700000))
    
