'''
Created on Dec 23, 2020

@author: brett_wood
'''

from node.blockchain.transaction_serialization import deserialize_transaction,\
    serialize_transaction
from utilities.serialization import deserialize_text
from utilities.sqlUtils import executeSql
from utilities.config import config
from binascii import unhexlify, hexlify
import ecdsa
from node.blockchain.queries import *
from collections import namedtuple
from node.blockchain.global_variables import *
from system_variables import address_search_url
import requests
from node.blockchain.contingency_operations import *
from utilities.hashing import calculateTransactionHash
from utilities.bitcoin_requests import getCurrentBitcoinBlockHeight
from node.blockchain.header_serialization import deserialize_block_header
from node.information.blocks import getMaxBlockHeight
from node.information.mempool import getMempoolInformation
from utilities.gis_functions import (
    queryPolygonEquality,
    queryPolygonRules,
    queryPolygonAreaMeters,
    queryUnionPolygonAreaMeters
    )

#input version 1 - standard spend (which could be a scuessful collateral)
#input version 2 - spending as collateral
#input version 3 - make claim
#input version 4 - spend failed transfer
#input version 5 - spend successful claim

#output version 1 - standard 
#output version 2 - collateral
#output version 3 - make claim

#UPDATE limit lat/long to 6 decimal places

def validateMempoolTransaction(transaction):
    
    transaction_hash_hex = hexlify(calculateTransactionHash(transaction)).decode('utf-8') 

    mempool_state = [True,'']
    
    mempool_search = getMempoolInformation(transaction_hash=transaction_hash_hex)
    if mempool_search != 'no_transaction_found':
        mempool_state = [False,'hash already exists in mempool']
        
    if mempool_state[0] == True:
        valid_transaction = validateTransaction(transaction)
        mempool_state = valid_transaction
    
    return mempool_state
    

def validateTransaction(transaction, block_height=None, block_header=None):
    
    transaction = deserialize_transaction(transaction)
    transaction_state = []
    
    transaction_type = transaction[0]
    transaction_type_int = int.from_bytes(transaction_type, byteorder='big')
    
    if (transaction_type_int == 1):
      transaction_state = validateTransaction1(transaction)
    
    elif (transaction_type_int == 2):
      transaction_state = validateTransaction2(transaction, block_height, block_header)
      
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
        else:
            print('validating landbase transaction: valid inputs (0)')
    
    #check only 1 output
    if (valid_transaction == True):
        valid_transaction = output_length == 1
        if(valid_transaction == False):
            failure_reason = 'outputs <> 1 in landbase transaction'
        else:
            print('validating landbase transaction: valid outputs (1)')
            
    #check output is version 4
    if (valid_transaction == True):
        valid_transaction = output_version == 0
        if(valid_transaction == False):
            failure_reason = 'wrong output version, needs to be 0 for landbase'
        else:
            print('validating landbase transaction: valid output version')
        
    #check only planet id 1
    if (valid_transaction == True):
        valid_transaction = planet_id == 1
        if(valid_transaction == False):
            failure_reason = 'planet_id <> 1'
        else:
            print('validating landbase transaction: valid planet')
    
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
            else:
                print('validating landbase transaction: valid geography')
        
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
        else:
            print('validating landbase transaction: valid contingencies')
    
    if failure_reason != '':
        print('validating landbase transaction: ' + failure_reason)
            
    return valid_transaction, failure_reason


def validateTransaction2(transaction, block_height, block_header):
    #standard transaction
    inputs = transaction[1]
    outputs = transaction[2]
    miner_fee_sats = int.from_bytes(transaction[3][0],'big')
    valid_transaction = True
    failure_reason = ''    
    
    try:
        #validate inputs
        valid_inputs = validateTransactionInputs(inputs, block_height, block_header, miner_fee_sats)
        if valid_inputs[0] == False:
            raise Exception(valid_inputs[0], valid_inputs[1])
        else:
            print('validating transaction: valid inputs')
       
        #validate input claims match output claims
        valid_outputs = validateInputOutputClaims(inputs, outputs)
        if valid_outputs[0] == False:
            raise Exception(valid_outputs[0], valid_outputs[1])
        else:
            print('validating transaction: valid claims')
        
        #validate shapes
        valid_shapes = validateShapes(inputs, outputs)
        if valid_shapes[0] == False:
            raise Exception(valid_shapes[0], valid_shapes[1])
        else:
            print('validating transaction: valid shapes')
        
        #UPDATE logic to check for planets when it expands beyond 1
        valid_outputs = validateTransactionOutputs(outputs)
        if valid_outputs[0] == False:
            raise Exception(valid_outputs[0], valid_outputs[1])
        else:
            print('validating transaction: valid outputs')
                
        #UPDATE validate contingency values
        #miner fee >= 0
        #miner fee blocks <=12096
        #transfer fee >= 0
        #transfer fee blocks <=12096
            
    except Exception as inst: 
        valid_transaction, failure_reason = inst.args  
        print("transaction status: " + str(valid_transaction))
        print("reason: " + str(failure_reason))
    
    if failure_reason != '':
        print('validating transaction: ' + failure_reason)
    
    return valid_transaction, failure_reason


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


def validateTransactionInputs(inputs, block_height, block_header, miner_fee_sats):
    
    valid_input = True
    failure_reason = ''

    input_length = len(inputs)
    for i in range(0, input_length):

        validate_input = validateTransactionInput(inputs[i],block_height, block_header, miner_fee_sats)
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

    for i in range(0, len(inputs)):
        input_version = int.from_bytes(inputs[i][0],'big')
        transaction_hash = hexlify(inputs[i][1]).decode('utf-8')
        transaction_vout = int.from_bytes(inputs[i][2],'big')
        if input_version == 3:
            input_claim_count = input_claim_count + 1
            output_parcel = getUtxo(transaction_hash=transaction_hash, vout=transaction_vout)
            input_shape_str = output_parcel.get('shape')
            input_claim_geom = "st_geomfromtext('" + input_shape_str + "',4326)"
    
    for i in range(0, len(outputs)):
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
    
    #logic that claim has to be 50% higher than previous one is captured in the input validation
    
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
    
    #validate that no more than 6 decimals are used and potentially other rules
    if (valid_shapes == True):
        valid_shapes = queryPolygonRules(outputs)
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
        output_parcel = getUtxo(transaction_hash=transaction_hash, vout=transaction_vout)
        shape_str = output_parcel.get('shape')
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


def validateTransactionInput(input, block_height, block_header, miner_fee_sats):
    
    input_version = int.from_bytes(input[0],'big')
    transaction_hash = hexlify(input[1]).decode('utf-8')
    transaction_vout = int.from_bytes(input[2],'big')
    input_signature = input[3]
    input_utxo = getUtxo(transaction_hash=transaction_hash, vout=transaction_vout)

    if block_height == None:
        block_height = getMaxBlockHeight() + 1

    if block_header != None:
        bitcoin_block_height = int.from_bytes(block_header[5],'big')
        
    else:
        bitcoin_block_height = getCurrentBitcoinBlockHeight()
       
        '''
        0 version,
        1 prev_block, 
        2 mrkl_root ,
        3 time_ ,
        4 bits ,
        5 bitcoin_height,
        6 miner_bitcoin_address,
        7 nonce
        '''
    
    inspected_parcel = inspectParcel(transaction_hash, transaction_vout, bitcoin_block_height, block_height)
    
    valid_input = True
    failure_reason = ''
    
    #validate it is an outstanding utxo
    if (valid_input == True):
        valid_input = input_utxo.get('status') != 'no utxo found'
        print(valid_input)
        if(valid_input == False):
            failure_reason = 'no utxo found'
    
    if (valid_input == True):

        input_utxo_version = input_utxo.get('output_version')
        input_utxo_id = input_utxo.get('id')
        input_utxo_shape = input_utxo.get('shape')
        input_utxo_pub_key = input_utxo.get('pub_key')
        input_utxo_collateral_pub_key = input_utxo.get('miner_landbase_address')
        input_utxo_failed_transfer_pub_key = input_utxo.get('transfer_fee_failover_address')
    
        #get summary of utxo - what is its transfer fee status, miner fee status
        #UPDATE to pull data from contingency logic
        transfer_fee_status = inspected_parcel.get('transfer_fee_status')
        claim_status = inspected_parcel.get('claim_status') #for investigating if a claim can be spent
        outstanding_claim = inspected_parcel.get('outstanding_claims')
        miner_fee_status = inspected_parcel.get('miner_fee_status')
        
        valid_transfer_fee_types = validContingencyStatusSpendTypes(input_version)[0]
        valid_miner_fee_types = validContingencyStatusSpendTypes(input_version)[1]
        valid_claim_types = validContingencyStatusSpendTypes(input_version)[2]
        valid_outstanding_claim_types = validContingencyStatusSpendTypes(input_version)[3]
        valid_input_utxo_types = validContingencyStatusSpendTypes(input_version)[4]
        
        transfer_fee_status_valid = ((transfer_fee_status in valid_transfer_fee_types) or valid_transfer_fee_types == [])
        miner_fee_status_valid = ((miner_fee_status in valid_miner_fee_types) or valid_miner_fee_types == [])
        claim_status_valid = ((claim_status in valid_claim_types) or valid_claim_types == [])
        outstanding_claim_valid = ((outstanding_claim in valid_outstanding_claim_types) or valid_outstanding_claim_types == [])
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
    #removed this because any claim i think can attempt to be made, it may just fail
    '''
    if (valid_input == True and input_version == 3):
        utxo_current_claim_sats = input_utxo.get('claim_fee_sats')
        valid_input = validateClaimAttempt(miner_fee_sats, utxo_current_claim_sats)
        if(valid_input == False):
            failure_reason = 'insufficient bid for claim'          
    '''
    
    #validate signature, but not for making a claim
    if (valid_input == True and input_version != 3):
        resolved_pub_key = getPublicKeySpendTypes(input_version, input_utxo_pub_key, input_utxo_failed_transfer_pub_key, input_utxo_collateral_pub_key)    
        
        input_utxo_shape_bytes = input_utxo_shape.encode('utf-8')
        resolved_pub_key_bytes = unhexlify(resolved_pub_key)
         
        valid_input = validateSignature(input_utxo_shape_bytes, resolved_pub_key_bytes, input_signature)
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
    #OPEN - fee not paid, but timing not expired
    #VALIDATED_UNCONFIRMED - fee was paid but not through the confirmation period
    #VALIDATED_CONFIRMED - fee was paid but not through the confirmation period
    #EXPIRED_UNCONFIRMED - fee not paid, timing expired, waiting for block period
    #EXPIRED_CONFIRMED - fee not paid, waiting period complete, parcel is returned to original address
    #NO_CLAIM, OUTSTANDING_CLAIM, SUCCESSFUL_CLAIM
    
    if spend_type == 1:
        transfer_fee_status = ['NO_CONTINGENCY', 'VALIDATED_CONFIRMED']
        miner_fee_status = ['NO_CONTINGENCY', 'VALIDATED_CONFIRMED']
        claim_status = []
        #outstanding_claim = ['NO_CLAIM', 'INVALIDATED_CLAIM', 'OUTSTANDING_CLAIM']
        outstanding_claim = ['UNCLAIMED']
        input_utxo_type = [0,1,2]
        
    elif spend_type == 2:
        transfer_fee_status = []
        miner_fee_status = ['EXPIRED_CONFIRMED']
        claim_status = []
        outstanding_claim = ['UNCLAIMED']
        input_utxo_type = [2]
        
    elif spend_type == 3:
        transfer_fee_status = ['NO_CONTINGENCY', 'VALIDATED_CONFIRMED', 'EXPIRED_CONFIRMED']
        miner_fee_status = ['NO_CONTINGENCY', 'VALIDATED_CONFIRMED', 'EXPIRED_CONFIRMED']
        claim_status = []
        outstanding_claim = ['UNCLAIMED']
        input_utxo_type = [0,1,2,3]
        
    elif spend_type == 4:
        transfer_fee_status = ['EXPIRED_CONFIRMED']
        miner_fee_status = []
        claim_status = []
        outstanding_claim = ['UNCLAIMED']
        input_utxo_type = [0,1,2]
    
    elif spend_type == 5:
        transfer_fee_status = []
        miner_fee_status = ['NO_CONTINGENCY', 'VALIDATED_CONFIRMED']
        claim_status = ['SUCCESSFUL']
        outstanding_claim = ['UNCLAIMED']
        input_utxo_type = [3]
    
    else:
        transfer_fee_status = 'error'
        miner_fee_status = 'error'
        claim_status = 'error'
        outstanding_claim = 'error'
        input_utxo_type = 'error'

    return transfer_fee_status, miner_fee_status, claim_status, outstanding_claim, input_utxo_type


def validateClaimAttempt(miner_fee_sats, utxo_current_claim_sats):
    
    if utxo_current_claim_sats == None or utxo_current_claim_sats == 0:
        return True
    
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


def addTransactionToMempool(transaction):

    deserialized_transaction = deserialize_transaction(transaction)

    version = int.from_bytes(deserialize_transaction(transaction)[0],'big')
    miner_fee_sats = int.from_bytes(deserialize_transaction(transaction)[3][0] ,'big')
    miner_fee_blocks = int.from_bytes(deserialize_transaction(transaction)[3][1] ,'big')
    transfer_fee_sats = int.from_bytes(deserialize_transaction(transaction)[3][2] ,'big')
    transfer_fee_blocks = int.from_bytes(deserialize_transaction(transaction)[3][3] ,'big')
    transfer_fee_address = deserialize_transaction(transaction)[3][4].decode('utf-8')
    
    #UPDATE as new transactions are added
    is_landbase = version == 1
    
    transaction_hash = calculateTransactionHash(transaction)
    transaction_hash = hexlify(transaction_hash).decode('utf-8')
    
    transaction_hex = hexlify(transaction).decode('utf-8')
    transaction_bytes = len(transaction)    

    query_insert_transaction_mempool = ("insert into bitland.transaction_mempool(transaction_hash, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address, transaction_serialized, byte_size) values "
                "('" + transaction_hash + "',"
                 + str(version) + ","
                 + str(is_landbase) + ","
                 + str(miner_fee_sats) + ","
                 + str(miner_fee_blocks) + ","
                 + str(transfer_fee_sats) + ","
                 + str(transfer_fee_blocks) + ","
                 + "'" + transfer_fee_address + "',"
                 + "'" + transaction_hex + "',"
                 + str(transaction_bytes) 
                + ") RETURNING id;"
                )    
    
    print(query_insert_transaction_mempool)
    
    try:
        transaction_mempool_id = executeSql(query_insert_transaction_mempool)[0]
    
    except Exception as error:
        print('error inserting transaction to mempool' + str(error))
    
    return transaction_mempool_id


if __name__ == '__main__':

    transaction = '000201013c75b4c2a69b3a86e13ac62705a6cf2d8a56d7d8b8d18bf846c621d62478fe060040ebff9ba202e4e182ed5d5fd685e4220279547ce2368f93a9453174def02b454d9c93667c18e65ed24968b181be63a38af117a3c0c5b59e7e94baf8c5b602f7d70101010054504f4c59474f4e28282d33392e3337352038372e373637312c2d33392e3337352038372e36323530382c2d34352038372e36323530382c2d34352038372e373637312c2d33392e3337352038372e37363731292940e3f2ecdefaa8e3f6652e8960dcca0d09d713fe255cbb5920c79e5dfe46f9447971cb2c76c7e6870ec9641924fa7a4ce7955bf911caf8be624cb21e4cfbcbfaf30000000000000000000000000000000000'
    transaction_bytes = unhexlify(transaction)
    deserialized_transaction = deserialize_transaction(transaction_bytes)
    print(deserialized_transaction[3][0])
    input = deserialize_transaction(transaction_bytes)[1][0]
    print(input)
    
    print(validateTransaction(transaction_bytes))
    
    #print(getUtxoTransferFeeStatus(6, 700000))
    #print(validateTransactionInput(input, 700000))
    
