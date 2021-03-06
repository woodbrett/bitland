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
from utilities.sql_utils import executeSql
from utilities.hashing import calculateHeaderHash, calculateTransactionHash
from node.blockchain.contingency_operations import *
from node.blockchain.mempool_operations import removeTransactionsFromMempool
from node.blockchain.global_variables import (
    contingency_validation_blocks,
    claim_required_percentage_increase
    )
import threading
from node.blockchain.validate_block import (
    validateBlock, 
    validateBlockHeader
    )
from node.information.blocks import (
    getBlockCount,
    getMaxBlockHeight,
    getBlock
    )
from node.information.utxo import (
    getUtxo
    )
from node.information.contingency import (
    getClaim,
    getExpiringCollateralTransactions,
    getExpiringTransferFeeTransactions
    )
from node.information.transaction import (
    getTransaction
    )
from utilities.bitcoin.bitcoin_transactions import countTransactionBlocks,\
    insertRelevantTransactions, synchWithBitcoin

def addBlock(block):
    
    block_height = getBlockCount() + 1
    print('saving block to database: ' + str(block_height))
    
    addSerializedBlock(block, block_height)
    print('added serialized block')
    
    addDeserializedBlock(block, block_height)
    print('added deserialized block')

    deserialized_block = deserializeBlock(block)
    transaction_count = len(deserialized_block[1])
    
    serialized_transactions = []
    for i in range(0, transaction_count):
        transaction_version = deserialized_block[1][i][0]
        transaction_inputs = deserialized_block[1][i][1]
        transaction_outputs = deserialized_block[1][i][2]
        transaction_contingencies = deserialized_block[1][i][3]
        serialized_transactions.append(serializeTransaction(transaction_version, transaction_inputs, transaction_outputs, transaction_contingencies))
        
    addTransactions(serialized_transactions, block_height)

    bitcoin_block = int.from_bytes(deserialized_block[0].get('bitcoin_height'),'big')
    prior_bitcoin_block_height = getBlock(block_id=block_height-1).get('bitcoin_block_height')

    #this step is very slow on some machines    
    updateContingenciesAndClaims(bitcoin_block, prior_bitcoin_block_height, block_height)
    print('updated contingencies')
    
    removeTransactionsFromMempool(block_height)
    print('removed transactions from mempool')
    
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
    header_hash = calculateHeaderHash(version,
        prev_block, 
        mrkl_root ,
        time_ ,
        bits ,
        bitcoin_hash,
        bitcoin_height,
        bitcoin_last_64_mrkl,
        miner_bitcoin_address,
        nonce)
    
    block_height = str(block_height)
    header_hash = str(hexlify(header_hash).decode('utf-8'))
    version = str(int.from_bytes(version, 'big'))
    prev_block = str(hexlify(prev_block).decode('utf-8'))
    mrkl_root = str(hexlify(mrkl_root).decode('utf-8'))
    time_ = str(int.from_bytes(time_, 'big'))
    bits = str(int.from_bytes(bits, 'big'))
    bitcoin_hash = str(hexlify(bitcoin_hash).decode('utf-8'))
    bitcoin_height = str(int.from_bytes(bitcoin_height, 'big'))
    bitcoin_last_64_mrkl = str(hexlify(bitcoin_last_64_mrkl).decode('utf-8'))
    miner_bitcoin_address = miner_bitcoin_address.decode('utf-8')
    nonce = str(int.from_bytes(nonce, 'big'))
    
    query_insert_deserialized_block = ("insert into bitland.block(id, header_hash, version, prev_block, mrkl_root, time, bits, bitcoin_hash, bitcoin_block_height, bitcoin_last_64_mrkl, miner_bitcoin_address,  nonce) values "
                "(" + block_height + "," +
                "'" + header_hash + "'," +
                version + "," +
                "'" + prev_block + "'," +
                "'" + mrkl_root + "'," +
                time_ + "," +
                bits + "," +
                "'" + header_hash + "'," + 
                bitcoin_height + "," +
                "'" + bitcoin_last_64_mrkl + "'," + 
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
        remove_block_query = ("select * from bitland.rollback_block(" + str(block_height) + ");")
        
        try:
            remove = executeSql(remove_block_query)[0]
            print(remove)
        
        except Exception as error:
            print('error removing block' + str(error))
            
        return True
    
    else:
        return False


def removeBlocks(low_block_height, high_block_height):
    
    for i in range(0, (high_block_height - low_block_height) + 1):
        
        remove = removeBlock(high_block_height - i)
        if remove == False:
            return False
    
    return True


def addTransactions(transaction_set, block_height):

    transaction_count = len(transaction_set)
    
    for i in range(0, transaction_count):
        addTransaction(transaction_set[i], block_height)
        #addSerializedTransaction()
        print('added transaction ' + str(i))
    
    return transaction_count


def addTransaction(transaction, block_height):

    version = int.from_bytes(deserializeTransaction(transaction)[0],'big')
    miner_fee_sats = int.from_bytes(deserializeTransaction(transaction)[3][0] ,'big')
    miner_fee_blocks = int.from_bytes(deserializeTransaction(transaction)[3][1] ,'big')
    transfer_fee_sats = int.from_bytes(deserializeTransaction(transaction)[3][2] ,'big')
    transfer_fee_blocks = int.from_bytes(deserializeTransaction(transaction)[3][3] ,'big')
    transfer_fee_address = deserializeTransaction(transaction)[3][4].decode('utf-8')
    
    #UPDATE as new transactions are added
    is_landbase = version == 1
    
    transaction_id = addTransactionHash(transaction, block_height, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address)
    inputs = deserializeTransaction(transaction)[1]
    inputs_len = len(inputs)
    outputs = deserializeTransaction(transaction)[2]
    outputs_len = len(outputs)
    claim_input_id = 0
    
    for i in range(0, inputs_len):
        input = inputs[i]
        input_version = int.from_bytes(input[0],'big')
        input_transaction_hash = hexlify(input[1]).decode('utf-8')
        input_transaction_id = getTransaction(transaction_hash=input_transaction_hash).get('id')
        vout = int.from_bytes(input[2],'big')
        vin = i
        output_parcel_id = getUtxo(transaction_hash=input_transaction_hash, vout=vout).get('id')
        sig = hexlify(input[3]).decode('utf-8')
        
        if input_version != 3:
            input_parcel_id = addParcelInput(transaction_id,vin, input_version,input_transaction_hash,input_transaction_id,vout,output_parcel_id,sig)
            
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

            status = 'OPEN'
            add_claim = addClaimToDb(claim_input_id, parcel_id, miner_fee_sats, block_height, status, block_height)

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


def addParcelInput(transaction_id, vin, input_version,input_transaction_hash,input_transaction_id,vout,output_parcel_id,sig):
    
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


#UPDATE to the new way of doing contingencies
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


#UPDATE to the new way of doing contingencies
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
        transfer_fee_status = calculateTransferFeeStatus(bitcoin_block=confirmed_bitcoin_block, transaction_id=transaction_id)
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


def updateContingenciesAndClaims(bitcoin_block_height, prior_bitcoin_block_height, bitland_block_height):
    
    if bitland_block_height == 1:
        return None

    inserted_transactions = insertRelevantTransactions(prior_bitcoin_block_height, bitcoin_block_height, bitland_block_height)
    
    #update contingencies
    updated_contingencies = updateContingencies(bitland_block_height, contingency_validation_blocks, bitcoin_block_height)
    
    #update claims
    updated_claims = updateClaims(bitcoin_block_height, contingency_validation_blocks, bitland_block_height, claim_blocks, claim_required_percentage_increase)
        
    return inserted_transactions


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
        print('no new landbases enabled' + str(error))    
    
    return parcel_id



if __name__ == '__main__':

    #00020101e0be7b649897a44097b1e4deea4e4eae470c6d0a3e20c411250aed5949607d420040e6c7bb4580dcdbb1ae71a53048416c4e734d9904bbefbb1e7896bee89504210f4d2ff562943bb955b10444dccd401d36ae4303c2c30eae064f6e24de47abccb60101010073504f4c59474f4e28282d3130312e3630313536332034382e35363838362c2d3130312e3630313536332034382e34333034342c2d3130312e3935333132352034382e34333034342c2d3130312e3935333132352034382e35363838362c2d3130312e3630313536332034382e3536383836292940c6d3ac0be14837a899218020c6d492fded6a9569832094f7b44232d7337fdbc108e7f8a3925fb7fd9ef39f91a95cd8eba9c82237c6e8a165b0b4a3872cfa15cb000000003a9800640000000036b0006522334e3645326e7072486d57436b333969626a336e774d5346354a3334655275704e62
    #00020101e0be7b649897a44097b1e4deea4e4eae470c6d0a3e20c411250aed5949607d420040937ac7aa01bbac0333d10fa68b5a9323e3832ece5107b57bff37b37e699611b2cf9906c753660eba300ad5027a694b3bb56aa2fdc28b161c9c4aa8e3e35dd46d0101010073504f4c59474f4e28282d3130312e3630313536332034382e35363838362c2d3130312e3630313536332034382e34333034342c2d3130312e3935333132352034382e34333034342c2d3130312e3935333132352034382e35363838362c2d3130312e3630313536332034382e3536383836292940c6d3ac0be14837a899218020c6d492fded6a9569832094f7b44232d7337fdbc108e7f8a3925fb7fd9ef39f91a95cd8eba9c82237c6e8a165b0b4a3872cfa15cb000000003a9800640000000036b000650b6164666173657766616573
    transaction = '00020101e0be7b649897a44097b1e4deea4e4eae470c6d0a3e20c411250aed5949607d4200406be9bd0812bfcbfe109b113dd33513f8b9bdcadd4978a237819dc955c42f341481fc3bd702405122373d9cd9ddc4ed16c9e959cc7bbef25329070c6399d1db460101010073504f4c59474f4e28282d3130312e3630313536332034382e35363838362c2d3130312e3630313536332034382e34333034342c2d3130312e3935333132352034382e34333034342c2d3130312e3935333132352034382e35363838362c2d3130312e3630313536332034382e3536383836292940c6d3ac0be14837a899218020c6d492fded6a9569832094f7b44232d7337fdbc108e7f8a3925fb7fd9ef39f91a95cd8eba9c82237c6e8a165b0b4a3872cfa15cb000000003a9800640000000036b0006522334e3645326e7072486d57436b333969626a336e774d5346354a3334655275704e62'
    transaction_bytes = unhexlify(transaction)
    print(addTransaction(transaction_bytes,1))




