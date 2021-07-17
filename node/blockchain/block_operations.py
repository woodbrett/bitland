'''
Created on Dec 23, 2020

@author: brett_wood
'''
from node.blockchain.header_operations import * 
from node.blockchain.transaction_operations import *
from node.blockchain.header_serialization import *
from node.blockchain.block_serialization import deserialize_block, serialize_block
from node.blockchain.transaction_serialization import serialize_transaction
from utilities.sqlUtils import executeSql
from node.blockchain.queries import *
from utilities.hashing import calculateHeaderHash, calculateTransactionHash
from node.blockchain.contingency_operations import *

def addBlock(block):
    
    block_height = getBlockCount() + 1
    
    addSerializedBlock(block, block_height)
    addDeserializedBlock(block, block_height)

    deserialized_block = deserialize_block(block)
    transaction_count = len(deserialized_block[1])
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = deserialized_block[1][i][0]
        transaction_inputs = deserialized_block[1][i][1]
        transaction_outputs = deserialized_block[1][i][2]
        transaction_contingencies = deserialized_block[1][i][3]
        serialized_transactions.append(serialize_transaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
        
    addTransactions(serialized_transactions, block_height)

    bitcoin_block = int.from_bytes(deserialized_block[0][5],'big')
    
    updateMinerFeeList(bitcoin_block, block_height)
    updateTransferFeeList(bitcoin_block, block_height)
    
    return(block_height)


def addSerializedBlock(block, block_height):
    
    block = hexlify(block).decode('utf-8')
    query_insert_serialized_block = "insert into bitland.block_serialized values (" + str(block_height) + ",'" + block + "') RETURNING id;"
    
    try:
        insert = executeSql(query_insert_serialized_block)[0]
    
    except Exception as error:
        print('error inserting serialized block' + str(error))
    
    return block_height


def addDeserializedBlock(block, block_height):

    header = deserialize_block_header(block)
        
    version = header[0]
    prev_block = header[1]
    mrkl_root = header[2]
    time_ = header[3]
    bits = header[4]
    bitcoin_height = header[5]
    miner_bitcoin_address = header[6]
    nonce = header[7]
    header_hash = calculateHeaderHash(version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_height,
        miner_bitcoin_address,
        nonce)
    
    block_height = str(block_height)
    header_hash = str(hexlify(header_hash).decode('utf-8'))
    version = str(int.from_bytes(version, 'big'))
    prev_block = str(hexlify(prev_block).decode('utf-8'))
    mrkl_root = str(hexlify(mrkl_root).decode('utf-8'))
    time_ = str(int.from_bytes(time_, 'big'))
    bits = str(int.from_bytes(bits, 'big'))
    bitcoin_height = str(int.from_bytes(bitcoin_height, 'big'))
    miner_bitcoin_address = str(unhexlify(miner_bitcoin_address).decode('utf-8'))
    nonce = str(int.from_bytes(nonce, 'big'))
    
    query_insert_deserialized_block = ("insert into bitland.block(id, header_hash, version, prev_block, mrkl_root, time, bits, bitcoin_block_height, miner_bitcoin_address, nonce) values "
                "(" + block_height + ","
                "'" + header_hash + "',"
                 + version + ","
                "'" + prev_block + "',"
                "'" + mrkl_root + "',"
                 + time_ + ","
                 + bits + ","
                 + bitcoin_height + ","
                "'" + miner_bitcoin_address + "',"
                 + nonce 
                + ") RETURNING id;"
                )    

    try:
        insert = executeSql(query_insert_deserialized_block)[0]
    
    except Exception as error:
        print('error inserting deserialized block' + str(error))
    
    return block_height


def removeBlock(block_height):
    
    max_block = getMaxBlockHeight()
    
    if block_height == max_block:
        remove_block_query = ("select * from bitland.rollback_block(" + block_height + ");")
        return True
    
    else:
        return False


def removeBlocks(low_block_height, high_block_height):
    
    for i in range(low_block_height, high_block_height):
        
        remove = removeBlock(high_block_height - i)
        if remove == False:
            return False
    
    return True


def addTransactions(transaction_set, block_height):

    transaction_count = len(transaction_set)
    
    for i in range(0, transaction_count):
        print(transaction_set[i])
        addTransaction(transaction_set[i], block_height)
    
    return transaction_count


def addTransaction(transaction, block_height):

    version = int.from_bytes(deserialize_transaction(transaction)[0],'big')
    miner_fee_sats = int.from_bytes(deserialize_transaction(transaction)[3][0] ,'big')
    miner_fee_blocks = int.from_bytes(deserialize_transaction(transaction)[3][1] ,'big')
    transfer_fee_sats = int.from_bytes(deserialize_transaction(transaction)[3][2] ,'big')
    transfer_fee_blocks = int.from_bytes(deserialize_transaction(transaction)[3][3] ,'big')
    transfer_fee_address = deserialize_transaction(transaction)[3][4].decode('utf-8')
    
    #UPDATE as new transactions are added
    is_landbase = version == 1
    
    transaction_id = addTransactionHash(transaction, block_height, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address)
    inputs = deserialize_transaction(transaction)[1]
    inputs_len = len(inputs)
    outputs = deserialize_transaction(transaction)[2]
    outputs_len = len(outputs)
    claim_input_id = 0
    
    for i in range(0, inputs_len):
        input = inputs[i]
        input_version = int.from_bytes(input[0],'big')
        input_transaction_hash = hexlify(input[1]).decode('utf-8')
        input_transaction_id = getTransactionIdByHash(input_transaction_hash)[0]
        vout = int.from_bytes(input[2],'big')
        vin = i
        output_parcel_id = getOutputParcelByTransactionVout(input_transaction_hash, vout)[3]
        sig = hexlify(input[3]).decode('utf-8')
        
        if input_version != 3:
            input_parcel_id = addParcelInput(transaction_id,vin, input_version,input_transaction_hash,input_transaction_id,vout,output_parcel_id,sig)

            #mark any invalidated claims
            #UPDATE can make this way more efficient by doing all transactions at once probably            
            override_claim_id = getClaimByOutputParcelId(output_parcel_id)
            if override_claim_id != 'no_claim':
                updateClaimInvalidate(override_claim_id, block_height, input_parcel_id)
            
        if input_version == 3:
            claim_input_id = output_parcel_id
        
    for i in range(0, outputs_len):
        output = outputs[i]
        
        output_version = int.from_bytes(output[0],'big')
        planet_id = int.from_bytes(output[1],'big')
        shape = output[2].decode('utf-8')
        pub_key = hexlify(output[3]).decode('utf-8')
        
        parcel_id = addParcelOutput(transaction_id, output_version, pub_key, i, planet_id, shape)
        
        if output_version == 3:
            #add new claims to DB
            leading_claim = 'true'
            invalidated_claim = 'false'
            add_claim = addClaimToDb(claim_input_id, parcel_id, miner_fee_sats, block_height, leading_claim, invalidated_claim, block_height)
        
            #mark superceded claims
            override_claim_id = getClaimByOutputParcelId(output_parcel_id)
            if override_claim_id != 'no_claim':
                updateClaimLeading(override_claim_id, block_height)

    if (is_landbase):
        updateDbLandbase(parcel_id, block_height)

    return transaction_id


def addTransactionHash(transaction, block_height, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address):
    
    block_height = str(block_height)
    
    version = str(version)
    is_landbase = str(is_landbase)
    miner_fee_sats = str(miner_fee_sats)
    miner_fee_blocks = str(miner_fee_blocks)
    transfer_fee_sats = str(transfer_fee_sats)
    transfer_fee_blocks = str(transfer_fee_blocks)
    transfer_fee_address = str(transfer_fee_address)
    
    transaction_hash = calculateTransactionHash(transaction)
    transaction_hash = hexlify(transaction_hash).decode('utf-8')
    
    query_insert_transaction_hash = ("insert into bitland.transaction(block_id, transaction_hash, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address) values "
                "(" + block_height + ","
                "'" + transaction_hash + "',"
                 + version + ","
                 + is_landbase + ","
                 + miner_fee_sats + ","
                 + miner_fee_blocks + ","
                 + transfer_fee_sats + ","
                 + transfer_fee_blocks + ","
                 + "'" + transfer_fee_address + "'"
                + ") RETURNING id;"
                )    
    
    try:
        transaction_id = executeSql(query_insert_transaction_hash)[0]
    
    except Exception as error:
        print('error inserting transaction hash' + str(error))
    
    return transaction_id


def addParcelOutput(transaction_id, output_version, pub_key, vout, planet_id, shape):
    
    transaction_id = str(transaction_id)
    output_version = str(output_version)
    pub_key = str(pub_key)
    vout = str(vout)
    planet_id = str(planet_id)
    shape = str(shape)
        
    query_insert_parcel_output = ("insert into bitland.output_parcel (transaction_id, output_version, pub_key, vout,planet_id, geom) values "
                "(" + transaction_id + ","
                 + output_version + ","
                "'" + pub_key + "',"
                 + vout + ","
                 + planet_id + ","
                 + "ST_GeomFromText('" + shape +"',4326)"
                + ") RETURNING id;"
                )    
    
    print(query_insert_parcel_output)
    
    try:
        parcel_id = executeSql(query_insert_parcel_output)[0]
    
    except Exception as error:
        print('error inserting output parcel' + str(error))
    
    return parcel_id


def addParcelInput(transaction_id, input_version,input_transaction_hash,input_transaction_id,vout,output_parcel_id,sig):
    
    transaction_id = str(transaction_id)
    vin = str(vin)
    input_version = str(input_version)
    input_transaction_hash = str(input_transaction_hash)
    input_transaction_id = str(input_transaction_id)
    vout = str(vout)
    output_parcel_id = str(output_parcel_id)
    sig = str(sig)
    
    query_insert_parcel_input = ("insert into bitland.input_parcel (transaction_id, vin, input_version, input_transaction_hash, input_transaction_id,vout, output_parcel_id, sig) values "
                "(" + transaction_id + ","
                 + vin + ","
                 + input_version + ","
                "'" + input_transaction_hash + "',"
                 + input_transaction_id + ","
                 + vout + ","
                 + output_parcel_id + ","
                + "'" + sig  + "'"
                + ") RETURNING id;"
                )    
    
    try:
        input_parcel_id = executeSql(query_insert_parcel_input)[0]
    
    except Exception as error:
        print('error inserting input parcel' + str(error))
    
    return input_parcel_id


def updateMinerFeeList(bitcoin_block, bitland_block):
    #look if any miner fees expired since last bitcoin block and then check on blockchain if they are successful or not
    confirmed_bitcoin_block = bitcoin_block - contingency_validation_blocks
    
    #1 query database to find utxos which expired before this block and haven't been recorded yet
    expiring_transaction_miner_fees = getExpiringCollateralTransactions(confirmed_bitcoin_block)
    print(expiring_transaction_miner_fees)

    for i in range(0, len(expiring_transaction_miner_fees)):
        
        transaction_id = expiring_transaction_miner_fees[i][0]
        print(transaction_id)

        #2 look in bitcoin blockchain to determine status
        miner_fee_status = calculateMinerFeeStatusTransaction(transaction_id, confirmed_bitcoin_block)
        #[status, txid, block_height, j, vout_address, value]
        
        print(miner_fee_status)
        
        bitcoin_block_height = miner_fee_status[2]
        bitcoin_transaction_hash = miner_fee_status[1]
        bitcoin_address = miner_fee_status[4]
        sats =  miner_fee_status[5]
        status =  miner_fee_status[0]
        bitland_block_height = bitland_block
        
        #3 add to database
        miner_status_id = addMinerFeeStatusToDb(transaction_id, bitcoin_block_height, bitcoin_transaction_hash, bitcoin_address, sats, status, bitland_block_height)
        
    #4 make it easy to roll this back, maybe put the recorded block into the table so it can be delete as part of the delete script
    
    return len(expiring_transaction_miner_fees)


def updateTransferFeeList(bitcoin_block, bitland_block):
    #similar to updating miner fee list
    
    confirmed_bitcoin_block = bitcoin_block - contingency_validation_blocks
    
    #1 query database to find utxos which expired before this block and haven't been recorded yet
    expiring_transaction_transfer_fees = getExpiringTransferFeeTransactions(confirmed_bitcoin_block)
    print(expiring_transaction_transfer_fees)

    for i in range(0, len(expiring_transaction_transfer_fees)):
        
        transaction_id = expiring_transaction_transfer_fees[i][0]
        print(transaction_id)

        #2 look in bitcoin blockchain to determine status
        transfer_fee_status = calculateTransferFeeStatusTransaction(transaction_id, confirmed_bitcoin_block)
        #[status, txid, block_height, j, vout_address, value]
        
        print(transfer_fee_status)
        
        bitcoin_block_height = transfer_fee_status[2]
        bitcoin_transaction_hash = transfer_fee_status[1]
        bitcoin_address = transfer_fee_status[4]
        sats =  transfer_fee_status[5]
        status =  transfer_fee_status[0]
        bitland_block_height = bitland_block
        
        #3 add to database
        transfer_status_id = addTransferFeeStatusToDb(transaction_id, bitcoin_block_height, bitcoin_transaction_hash, bitcoin_address, sats, status, bitland_block_height)
        
    #4 make it easy to roll this back, maybe put the recorded block into the table so it can be delete as part of the delete script
    
    return len(expiring_transaction_transfer_fees)


def updateDbLandbase(parcel_id, block_height):
    
    parcel_id = str(parcel_id)
    block_height = str(block_height)
    
    query_update_landbase_claim = (
                "with landbase_id as ( " +
                "select le.id " +
                "from bitland.output_parcel op " +
                "join bitland.landbase_enum le on st_intersects(op.geom, le.geom) " +
                "  and valid_claim is true " +
                "  and st_equals(op.geom, le.geom) " + 
                "  and op.id = " + parcel_id +
                ") " +
                "update bitland.landbase_enum le " +
                "set block_claim = " + block_height + " , valid_claim = false " +
                "from landbase_id li " +
                "where li.id = le.id returning 1; ")
    
    try:
        landbase_claim = executeSql(query_update_landbase_claim)[0]
    
    except Exception as error:
        print('error updating landbase claim' + str(error))        
        

    query_update_valid_landbase = (
                "with landbase_id as ( " +
                "select le.id " +
                "from bitland.output_parcel op " +
                "join bitland.landbase_enum le on st_touches(op.geom, le.geom) " +
                "  and valid_claim is false " +
                "  and block_claim is null " +
                "  and op.id = " + parcel_id +
                ") " +
                "update bitland.landbase_enum le " +
                "set valid_claim = true, valid_enabled_block = " + block_height + " " +
                "from landbase_id li " +
                "where li.id = le.id returning 1; ")
    
    try:
        landbase_claim = executeSql(query_update_valid_landbase)[0]
    
    except Exception as error:
        print('error updating landbase valid update' + str(error))    
    
    return parcel_id


if __name__ == '__main__':
    
    print(updateMinerFeeList(700000,4))
    print(updateTransferFeeList(700000,4))
    
    '''
    block = '0001000000000000000000000000000000000000000000000000000000000000000045cdd9a625301abded768599cbaa8bc321b8c744699940fbf954f78af934872300603b3c0d1d0ffff0000a42f931354e77556b745a74346b574d4c714b35514c7278414d51617079654678416936680c0d56b00001000101010033504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c3020393029298064663865373761643166393165313261313435616661646130393737373239396332396234656332323535376465376266643737626261306163663836306137633735373766666130313238313638396363346530396330646439636361343734323336656264653364633134623430333234346365366532393763643531360000000000000000000000000000000000'
    block_bytes = unhexlify(block)

    #addBlock(block_bytes)
    
    deserialized_block = deserialize_block(block_bytes)
    transaction_count = len(deserialized_block[1])
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = deserialized_block[1][i][0]
        transaction_inputs = deserialized_block[1][i][1]
        transaction_outputs = deserialized_block[1][i][2]
        transaction_contingencies = deserialized_block[1][i][3]
        serialized_transactions.append(serialize_transaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
    
    print(addTransactions(serialized_transactions, 1))
    '''
    
    