'''
Created on Dec 23, 2020

@author: brett_wood
'''
from node.blockchain.header_operations import *
from node.blockchain.transaction_operations import *
from node.blockchain.header_serialization import *
from node.blockchain.block_serialization import (
    deserializeBlock, 
    serializeBlock
    )
from node.blockchain.transaction_serialization import serializeTransaction
from node.blockchain.queries import *
from collections import Counter
from node.information.blocks import (
    getMaxBlockHeight, 
    getBlock,
    getBlockSerialized
    )


def validateBlock(block, realtime_validation=True, prev_block_input=None):
#realtime validation indicates if it is validating the head of the chain in realtime
#which impacts some of the timing elements that it analyzes vs synching old blocks
#prev_block_input allows you to submit the previous block as an input rather than fetching from the database

    valid_block = True
    
    print('validating block header')
    validate_block = validateBlockHeader(block, realtime_validation, prev_block_input)
    
    valid_block = validate_block[0]
    print("block header valid: " + str(valid_block))
    new_block_height = getMaxBlockHeight() + 1
    
    if (valid_block == True):
        print('validating transactions')
        valid_block = validateTransactions(block, new_block_height)[0]
        print("transactions valid: " + str(valid_block))
    
    return valid_block


def validateBlockHeader(block, realtime_validation=True, prior_block=None):
 
    header = deserializeBlockHeader(block)

    header = deserializeBlockHeader(block)
        
    version = header.get('version')
    prev_block = header.get('prev_block')
    mrkl_root = header.get('mrkl_root')
    time_ = header.get('time')
    bits = header.get('bits')
    bitcoin_hash = header.get('bitcoin_hash')
    bitcoin_height = header.get('bitcoin_height')
    bitcoin_last_64_mrkl = header.get('bitcoin_last_64_mrkl')
    miner_bitcoin_address = header.get('miner_bitcoin_address')
    nonce = header.get('nonce')
    
    header_serialized = serializeBlockHeader(version, prev_block, mrkl_root, time_, bits, nonce, bitcoin_hash, bitcoin_height, bitcoin_last_64_mrkl, miner_bitcoin_address)
    
    deserialized_block = deserializeBlock(block)
    transaction_count = len(deserialized_block[1])
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = deserialized_block[1][i][0]
        transaction_inputs = deserialized_block[1][i][1]
        transaction_outputs = deserialized_block[1][i][2]
        transaction_contingencies = deserialized_block[1][i][3]
        serialized_transactions.append(serializeTransaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
    
    #prior block calculations for validation
    if prior_block == None:
        
        #prev_block_hex = hexlify(prev_block).decode('utf-8')
        #prior_block_height = getBlock(header_hash=prev_block_hex).get('id')
        prior_block_height = getMaxBlock()
        prior_block_hex = getBlockSerialized(prior_block_height)
        prior_block = unhexlify(prior_block_hex)
    
    prior_block_header = deserializeBlockHeader(prior_block)
    prior_block_hash = calculateHeaderHashFromBlock(block_bytes=prior_block)
    prior_block_bitcoin_height = prior_block_header.get('bitcoin_height')
    
    valid_header = True
    failure_reason = ''
    
    if (valid_header == True):
        valid_header = validateVer(version)
        if(valid_header == False):
            failure_reason = 'invalid version'
        else:
            print('validating block header: valid version')
    
    if (valid_header == True):
        valid_header = validatePrevBlock(prev_block, prior_block_hash)
        if(valid_header == False):
            failure_reason = 'invalid previous block'
        else:
            print('validating block header: valid previous block')
    
    if (valid_header == True):
        valid_header = validateMrklRoot(mrkl_root, serialized_transactions)   
        if(valid_header == False):
            failure_reason = 'invalid merkle root'
        else:
            print('validating block header: valid merkle root')
            
    if (valid_header == True):
        valid_header = validateTime(time_, realtime_validation)    
        if(valid_header == False):
            failure_reason = 'invalid timestamp'
        else:
            print('validating block header: valid timestamp')
    
    if (valid_header == True):
        valid_header = validateBitcoinHash(bitcoin_hash, bitcoin_height)    
        if(valid_header == False):
            failure_reason = 'invalid bitcoin hash'
        else:
            print('validating block header: valid bitcoin hash')

    if (valid_header == True):
        valid_header = validateBitcoinBlock(bitcoin_height, prior_block_bitcoin_height, realtime_validation)    
        if(valid_header == False):
            failure_reason = 'invalid bitcoin block height'
        else:
            print('validating block header: valid bitcoin block height')
    
    if (valid_header == True):
        valid_header = validateBitcoinLast64Mrkl(bitcoin_last_64_mrkl, bitcoin_height)    
        if(valid_header == False):
            failure_reason = 'invalid last 64 bitcoin hashes merkle root'
        else:
            print('validating block header: valid last 64 bitcoin hashes merkle root')
    
    if (valid_header == True):
        valid_header = validateBits(bits)    
        if(valid_header == False):
            failure_reason = 'invalid bits'
        else:
            print('validating block header: valid bits')
    
    if (valid_header == True):
        valid_header = validateBitcoinAddress(miner_bitcoin_address)      
        if(valid_header == False):
            failure_reason = 'invalid bitcoin address'   
        else:
            print('validating block header: valid bitcoin address')
      
    if (valid_header == True):
        valid_header = validateHeaderHash(version ,prev_block, mrkl_root ,time_,bits, bitcoin_hash, bitcoin_height,bitcoin_last_64_mrkl,miner_bitcoin_address,nonce )  
        if(valid_header == False):
            failure_reason = 'invalid header hash' 
        else:
            print('validating block header: valid header hash')
    
    if failure_reason != '':
        print ('validating block header: ' + failure_reason)
        
    return valid_header, failure_reason


def validateTransactions(block=b'', block_height=None, transactions=[]):
#block height represents the next block, e.g. the current block hegiht + 1

    if transactions != []:
        header = None
        
    else:
        deserialized_block = deserializeBlock(block)
        header = deserialized_block[0]
        transactions = deserialized_block[1]

    transaction_count = len(transactions)
    print('transaction count: ' + str(transaction_count))
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = transactions[i][0]
        transaction_inputs = transactions[i][1]
        transaction_outputs = transactions[i][2]
        transaction_contingencies = transactions[i][3]
        serialized_transactions.append(serializeTransaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
    
    valid_transactions = [True, '', 0]
    transaction_input_utxo = []
    all_transaction_type = []
    
    for i in range(0, len(serialized_transactions)):
        print('validating transaction ' + str(i))
        transaction_status = validateTransaction(serialized_transactions[i], block_height, header)
        valid_transactions=[transaction_status[0], transaction_status[1], i]
        
        transaction_inputs = deserializeTransaction(serialized_transactions[i])[1]
        transaction_type = deserializeTransaction(serialized_transactions[i])[0]
        
        all_transaction_type.append(transaction_type)
        
        for j in range(0, len(transaction_inputs)):
            transaction_hash = hexlify(transaction_inputs[j][1]).decode('utf-8')
            transaction_vout = int.from_bytes(transaction_inputs[j][2],'big')
            input_utxo_id = getUtxo(transaction_hash=transaction_hash, vout=transaction_vout).get('id')
            transaction_input_utxo.append(input_utxo_id)
        
        if (valid_transactions[0] == False):
            current_transaction_hash = calculateTransactionHash(serialized_transactions[i])
            print(current_transaction_hash)
            valid_transactions = [False, 'invalid transaction ' + str(hexlify(current_transaction_hash).decode('utf-8')), 0]
            break
    
    #UPDATE validate that inputs aren't in multiple transactions in the block    
    if (valid_transactions[0] == True): 
        utxo_count_list = Counter(transaction_input_utxo)
        greater_one_utxo = 0
        
        for key in utxo_count_list: 
            if utxo_count_list[key] > 1: 
                greater_one_utxo = greater_one_utxo + 1
    
        if greater_one_utxo > 0:
            valid_transactions = [False, 'double spent utxo in block', 0]
    
    #UPDATE validate no more than 1 landbase transaction
    if (valid_transactions[0] == True): 
        landbase_counter = 0
        for i in range(0, len(all_transaction_type)): 
            if all_transaction_type[i] == 1: 
                landbase_counter = landbase_counter + 1
    
        if landbase_counter > 1:
            valid_transactions = [False, '>1 landbase transactions', 0]    
    
    #UPDATE validate that no claims are made on same utxo with same claim amount (can be on same utxo though)
    
    return valid_transactions

   