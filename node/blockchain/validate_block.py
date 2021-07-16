'''
Created on Dec 23, 2020

@author: brett_wood
'''
from node.blockchain.header_operations import *
from node.blockchain.transaction_operations import *
from node.blockchain.header_serialization import *
from node.blockchain.block_serialization import deserialize_block, serialize_block
from node.blockchain.transaction_serialization import serialize_transaction
from node.blockchain.queries import *
from collections import Counter


def validateBlock(block, realtime_validation=True):
#realtime validation indicates if it is validating the head of the chain in realtime
#which impacts some of the timing elements that it analyzes vs synching old blocks

    valid_block = True
    
    validate_block = validateBlockHeader(block, realtime_validation)
    print(validate_block)
    
    valid_block = validate_block[0]
    
    if (valid_block == True):
      valid_block = validateTransactions(block)[0]
    
    return valid_block


def validateBlockHeader(block, realtime_validation=True):

    header = deserialize_block_header(block)
        
    version = header[0]
    prev_block = header[1]
    mrkl_root = header[2]
    time_ = header[3]
    bits = header[4]
    bitcoin_height = header[5]
    miner_bitcoin_address = header[6]
    nonce = header[7]
    
    header_serialized = serialize_block_header(version, prev_block, mrkl_root, time_, bits, nonce, bitcoin_height, miner_bitcoin_address)
    
    deserialized_block = deserialize_block(block)
    transaction_count = len(deserialized_block[1])
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = deserialized_block[1][i][0]
        transaction_inputs = deserialized_block[1][i][1]
        transaction_outputs = deserialized_block[1][i][2]
        transaction_contingencies = deserialized_block[1][i][3]
        serialized_transactions.append(serialize_transaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
        
    print(serialized_transactions)    
    
    valid_header = True
    failure_reason = ''
    
    if (valid_header == True):
        valid_header = validateVer(version)
        if(valid_header == False):
            failure_reason = 'invalid version'
    
    if (valid_header == True):
        valid_header = validatePrevBlock(prev_block)
        if(valid_header == False):
            failure_reason = 'invalid previous block'
    
    if (valid_header == True):
        valid_header = validateMrklRoot(mrkl_root, serialized_transactions)   
        if(valid_header == False):
            failure_reason = 'invalid merkle root'
            
    if (valid_header == True):
        valid_header = validateTime(time_, realtime_validation)    
        if(valid_header == False):
            failure_reason = 'invalid timestamp'
    
    if (valid_header == True):
        valid_header = validateBitcoinBlock(bitcoin_height, realtime_validation)    
        if(valid_header == False):
            failure_reason = 'invalid bitcoin block height'
    
    if (valid_header == True):
        valid_header = validateBits(bits)    
        if(valid_header == False):
            failure_reason = 'invalid bits'
    
    if (valid_header == True):
        valid_header = validateBitcoinAddress(miner_bitcoin_address)      
        if(valid_header == False):
            failure_reason = 'invalid bitcoin address'   
      
    if (valid_header == True):
        valid_header = validateHeaderHash(version ,prev_block, mrkl_root ,time_,bits ,bitcoin_height ,miner_bitcoin_address,nonce )  
        if(valid_header == False):
            failure_reason = 'invalid header hash' 
     
    return valid_header, failure_reason


#UPDATE think this can be removed
'''
def validateBlockHeaderSynch(header):

    header = deserialize_block_header(header)
        
    version = header[0]
    prev_block = header[1]
    mrkl_root = header[2]
    time_ = header[3]
    bits = header[4]
    bitcoin_height = header[5]
    miner_bitcoin_address = header[6]
    nonce = header[7]
    
    header_serialized = serialize_block_header(version, prev_block, mrkl_root, time_, bits, nonce, bitcoin_height, miner_bitcoin_address)
    
    valid_header = True
    failure_reason = ''
    
    if (valid_header == True):
        valid_header = validateVer(version)
        if(valid_header == False):
            failure_reason = 'invalid version'
    
    if (valid_header == True):
        valid_header = validatePrevBlock(prev_block)
        if(valid_header == False):
            failure_reason = 'invalid previous block'
    
    if (valid_header == True):
        valid_header = validateMrklRoot(mrkl_root, serialized_transactions)   
        if(valid_header == False):
            failure_reason = 'invalid merkle root'
            
    if (valid_header == True):
        valid_header = validateTimeHistorical(time_)    
        if(valid_header == False):
            failure_reason = 'invalid timestamp'
    
    if (valid_header == True):
        valid_header = validateBitcoinBlockHistorical(bitcoin_height)    
        if(valid_header == False):
            failure_reason = 'invalid bitcoin block height'
    
    #will need to make this historical
    if (valid_header == True):
        valid_header = validateBits(bits)    
        if(valid_header == False):
            failure_reason = 'invalid bits'
    
    if (valid_header == True):
        valid_header = validateBitcoinAddress(miner_bitcoin_address)      
        if(valid_header == False):
            failure_reason = 'invalid bitcoin address'   
      
    if (valid_header == True):
        valid_header = validateHeaderHash(version ,prev_block, mrkl_root ,time_,bits ,bitcoin_height ,miner_bitcoin_address,nonce )  
        if(valid_header == False):
            failure_reason = 'invalid header hash' 
     
    return valid_header, failure_reason
'''


def validateTransactions(block):

    deserialized_block = deserialize_block(block)
    transaction_count = len(deserialized_block[1])
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = deserialized_block[1][i][0]
        transaction_inputs = deserialized_block[1][i][1]
        transaction_outputs = deserialized_block[1][i][2]
        transaction_contingencies = deserialized_block[1][i][3]
        serialized_transactions.append(serialize_transaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
    
    valid_transactions = [True, '', 0]
    transaction_input_utxo = []
    all_transaction_type = []
    
    for i in range(0, len(serialized_transactions)):
        transaction_status = validateTransaction(serialized_transactions[i])
        valid_transactions=[transaction_status[0], transaction_status[1], i]
        
        transaction_inputs = deserialize_transaction(serialized_transactions[i])[1]
        transaction_type = deserialize_transaction(serialized_transactions[i])[0]
        print(transaction_inputs)
        
        all_transaction_type.append(transaction_type)
        
        for j in range(0, len(transaction_inputs)):
            transaction_hash = hexlify(transaction_inputs[j][1]).decode('utf-8')
            transaction_vout = int.from_bytes(transaction_inputs[j][2],'big')
            input_utxo_id = getOutputParcelByTransactionVout(transaction_hash, transaction_vout)[3]
            transaction_input_utxo.append(input_utxo_id)
        
        if (valid_transactions[0] == False):
            break
    
    #UPDATE validate that inputs aren't in multiple transactions in the block    
    if (valid_transactions[0] == True): 
        utxo_count_list = Counter(transaction_input_utxo)
        print(utxo_count_list)
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
    
    return valid_transactions


if __name__ == '__main__':

    block = '000100000005ab13d277f22aab57a694f8e38dc900a2ba373ebe9fbba919c93aa74ab0bcaa0b93e0802533596449a9efa39f7137895c51baba2fa3eefe38cab8fff600603db5521d0ffff0000a43f031354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680946fe420001000101010052504f4c59474f4e28282d32322e352038392e333638322c2d32322e352038392e313436382c2d33332e37352038392e313436382c2d33332e37352038392e333638322c2d32322e352038392e33363832292940fddb35232e67e57e896fc91e81435564777ee5e78291ee1bbf708a80aeff9fa7ff6d82de884cec86f35932774b2eabfed527e1d0b0278c23e2e22fe6e9887b160000000000000000000000000000000000000201010bc06709774a5c7a5dd292c451ededbee378340df618351f4abbdf077cd3d18f00401247cfe2a12d96481d8136d82264b9d127aaffcdd0fa611acfcaa1cc820ea83e661a4735328c91a53e90407b737a76693a9a257eeb0b7d876a564f1aabfe633d020101002c504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c302039302929409a19a65bc5b1fe8c3c4a60d5b2dbcbde27af0505b62a5ed46b3dc73e777202e8dbd6226eca1bb60bafdea37efc09a6faddf95bf22f699628b539948ddc372a8b02010030504f4c59474f4e28282d39302038392e37343637342c2d39302039302c302039302c2d39302038392e37343637342929401e410b1ecfb51fea3cd62bdf82107e54dddaf93629163b0365aba0b69406a987ac1bc3f5fd1cf812e4bfca854cfc3ec068402b7ec8ee2c73a66b1dd63032ebb800000000271007d000000007a12001902a626331716571723335646c723266616d6870797738763939767972707834376d67707378726c67786378'
    block_bytes = unhexlify(block)
    
    print(validateTransactions(block_bytes))
    
    
    