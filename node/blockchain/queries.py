'''
Created on Feb 15, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from collections import namedtuple

#UPDATE - is this needed?
def addContingencyStatusToDb(status, output_parcel_id ,  output_parcel_type , contingency_transaction_id , contingency_fee_vout , contingency_block_height, recorded_status_bitcoin_block_height ,recorded_status_bitland_block_height):

    status = str(status)
    output_parcel_id = str(output_parcel_id)
    output_parcel_type = str(output_parcel_type) 
    contingency_transaction_id =  str(contingency_transaction_id)
    contingency_fee_vout =  str(contingency_fee_vout)
    contingency_block_height =  str(contingency_block_height)
    recorded_status_bitcoin_block_height =  str(recorded_status_bitcoin_block_height)
    recorded_status_bitland_block_height =  str(recorded_status_bitland_block_height)
    
    query = ("insert into bitland.contingency_status (  status, output_parcel_id ,  output_parcel_type , contingency_transaction_id , contingency_fee_vout , contingency_block_height, recorded_status_bitcoin_block_height ,recorded_status_bitland_block_height) values " +
            "('" + status + "'," +
            output_parcel_id + "," +  
            output_parcel_type + "," + 
            "'" + contingency_transaction_id +"'," + 
            contingency_fee_vout + "," + 
            contingency_block_height + "," + 
            recorded_status_bitcoin_block_height + "," + 
            recorded_status_bitland_block_height + ") "
            "RETURNING output_parcel_id;"
            )
    
    output_parcel_id = executeSql(query)
    
    return output_parcel_id


def addMinerFeeStatusToDb(transaction_id, bitcoin_block_height, bitcoin_transaction_hash, bitcoin_address, sats, status, bitland_block_height):

    transaction_id = str(transaction_id)
    bitcoin_block_height = str(bitcoin_block_height)
    bitcoin_transaction_hash = str(bitcoin_transaction_hash) 
    bitcoin_address =  str(bitcoin_address)
    sats =  str(sats)
    status =  str(status)
    bitland_block_height =  str(bitland_block_height)
    
    query = ("insert into bitland.miner_fee_transaction(transaction_id, bitcoin_block_height, bitcoin_transaction_hash, bitcoin_address, sats, status, bitland_block_height) values " +
            "(" + transaction_id + "," +
            bitcoin_block_height + "," +  
            "'" + bitcoin_transaction_hash + "'," + 
            "'" + bitcoin_address + "'," + 
            sats + "," + 
            "'" + status + "'," + 
            bitland_block_height + ") "
            "RETURNING id;"
            )
    
    miner_fee_status_id = executeSql(query)
    
    return miner_fee_status_id


def addTransferFeeStatusToDb(transaction_id, bitcoin_block_height, bitcoin_transaction_hash, bitcoin_address, sats, status, bitland_block_height):

    transaction_id = str(transaction_id)
    bitcoin_block_height = str(bitcoin_block_height)
    bitcoin_transaction_hash = str(bitcoin_transaction_hash) 
    bitcoin_address =  str(bitcoin_address)
    sats =  str(sats)
    status =  str(status)
    bitland_block_height =  str(bitland_block_height)
    
    query = ("insert into bitland.transfer_fee_transaction(transaction_id, bitcoin_block_height, bitcoin_transaction_hash, bitcoin_address, sats, status, bitland_block_height) values " +
            "(" + transaction_id + "," +
            bitcoin_block_height + "," +  
            "'" + bitcoin_transaction_hash + "'," + 
            "'" + bitcoin_address + "'," + 
            sats + "," + 
            "'" + status + "'," + 
            bitland_block_height + ") "
            "RETURNING id;"
            )
    
    print(query)
    
    miner_fee_status_id = executeSql(query)
    
    return miner_fee_status_id


#What is invalidation input parcel id?
def addClaimToDb(claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, leading_claim, invalidated_claim, invalidation_input_parcel_id, from_bitland_block_height):

    claimed_output_parcel_id = str(claimed_output_parcel_id)
    claim_action_output_parcel_id = str(claim_action_output_parcel_id)
    claim_fee_sats = str(claim_fee_sats) 
    claim_block_height =  str(claim_block_height)
    leading_claim =  str(leading_claim)
    invalidated_claim =  str(invalidated_claim)
    from_bitland_block_height =  str(from_bitland_block_height)
    
    query = ("insert into bitland.claim (claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, leading_claim, invalidated_claim,from_bitland_block_height) values " +
            "(" + claimed_output_parcel_id + "," +
            claim_action_output_parcel_id + "," +  
            claim_fee_sats + "," +  
            claim_block_height + "," +  
            "'" + leading_claim + "'," + 
            "'" + invalidated_claim + "'," + 
            from_bitland_block_height + ") "
            "RETURNING id;"
            )
    
    claim_id = executeSql(query)
    
    return claim_id


def updateClaimInvalidate(id, block, invalidation_parcel_id):
    
    id = str(id)
    block = str(block)
    invalidation_parcel_id = str(invalidation_parcel_id)
    
    query = ("update bitland.claim set invalidated_claim = true, to_bitland_block_height = " + block + ", invalidation_input_parcel_id = " + invalidation_parcel_id + " where id = " + id + " RETURNING id")
    claim_id = executeSql(query)[0]
    
    return claim_id


def updateClaimLeading(id, block):
    
    id = str(id)
    block = str(block)
    
    query = ("update bitland.claim set leading_claim = false, to_bitland_block_height = " + block + " where id = " + id + " RETURNING id")
    claim_id = executeSql(query)[0]
    
    return claim_id


def countUnspentParcel(transaction_hash, vout):
    
    select = ("select count(*) from bitland.unspent_parcel" 
    + "\n where transaction_hash = '" + transaction_hash + "' and vout = " + str(vout) + ";")
    
    parcel_info = executeSql(select)
    return parcel_info


def AddParcel(
        planet_id,
        parcel_key,
        parcel_hash,
        shape
        ):
    
    geom = "ST_Geomfromtext('" + shape + "'::varchar)"
    
    insert_parcel = ("insert into bitland.parcel( planet_id,parcel_key, parcel_hash,shape, geom ) values "
                "(" + str(planet_id) + ","
                "'" + parcel_key + "',"
                "'" + parcel_hash + "',"
                "'" + shape + "',"
                + geom + ") "
                "RETURNING id;"
                )
    
    parcel_id = executeSql(insert_parcel)

    return parcel_id[0]


def getMaxBlock():

    return executeSql('select * from bitland.max_block;')[0]


def getPriorBlock():
    max_block = getMaxBlock()
    select = ('select header_hash, bits, id from bitland.block b where id = ' + str(max_block) + ';')
    return executeSql(select)


def getBlockById(block_id):
    select = ("select * from bitland.block b where id = " + str(block_id) + ";")
    return executeSql(select)


def getBlockInformation(block_id = -1, header_hash = ''):
    select = ("select id, header_hash , version, prev_block , mrkl_root , time, bits, bitcoin_block_height , miner_bitcoin_address, nonce from bitland.block b "
              +" where id = " + str(block_id) + " or header_hash = '" + str(header_hash) + "' ;")
    
    try:
        db_block = executeSql(select)
        columns = namedtuple('columns', ['id', 'header_hash', 'version', 'prev_block', 'mrkl_root', 'time', 'bits', 'bitcoin_block_height', 'miner_bitcoin_address', 'nonce'])
        block = columns(
                        db_block[0],
                        db_block[1],
                        db_block[2],
                        db_block[3],
                        db_block[4],
                        db_block[5],
                        db_block[6],
                        db_block[7],
                        db_block[8],
                        db_block[9]
                        )

    except Exception as error:
        print('no block_found' + str(error))
        block = 'no block_found'
    
    return block 


def getBlockHeaders(start_block_height, end_block_height):
    start_block_height = str(start_block_height)
    end_block_height = str(end_block_height)
    select = ("select header_hash from bitland.block where id between " + start_block_height + " and " + end_block_height + " ;")
    return executeSqlMultipleRows(select)

#UPDATE - may be more elegant to get transactions from that table vs distincting UTXOs
def getExpiringCollateralTransactions(bitcoin_block_id):
    select = ("select id from bitland.transaction_contingency where miner_fee_sats <> 0 and miner_fee_status is null and bitcoin_block_height + miner_fee_blocks < " + str(bitcoin_block_id) + ";")
    return executeSqlMultipleRows(select)


def getExpiringTransferFeeTransactions(bitcoin_block_id):
    select = ("select id from bitland.transaction_contingency where transfer_fee_sats <> 0 and transfer_fee_status is null and bitcoin_block_height + miner_fee_blocks < " + str(bitcoin_block_id) + ";")
    return executeSqlMultipleRows(select)
    

def getContingencyStatus(output_id):
    output_id = str(output_id)
    select = ("select status, output_parcel_id, output_parcel_type, contingency_transaction_id, contingency_fee_vout, contingency_block_height, recorded_status_bitcoin_block_height ,recorded_status_bitland_block_height from bitland.contingency_status where output_parcel_id = " + str(output_id) + ";")
    
    try:
        contingency_sql = executeSql(select)
        columns = namedtuple('columns', ['status', 'output_parcel_id', 'output_parcel_type', 'contingency_transaction_id', 'contingency_fee_vout', 'contingency_block_height', 'recorded_status_bitcoin_block_height', 'recorded_status_bitland_block_height'])
        contingency_output = columns(
                        contingency_sql[0],
                        contingency_sql[1],
                        contingency_sql[2],
                        contingency_sql[3],
                        contingency_sql[4],
                        contingency_sql[5],
                        contingency_sql[6],
                        contingency_sql[7]
                        )
        
    except Exception as error:
        print('no contingency record found for output' + str(error))
        columns = namedtuple('columns', ['status'])
        contingency_output = columns(
                        'no contingency db records for output')
    
    return contingency_output  
      
              

def getMedianBlockTime11():
    
    select = ("with max_id as ("
        "\n select max(id) as max_id from bitland.block"
        "\n )"
        "\n select PERCENTILE_CONT(0.5) within group(ORDER BY b.time)"
        "\n from max_id m"
        "\n join bitland.block b on b.id >= (m.max_id - 10)")
    
    median_time_11 = executeSql(select)[0]

    return median_time_11

