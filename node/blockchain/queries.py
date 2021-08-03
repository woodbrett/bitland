'''
Created on Feb 15, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from collections import namedtuple
    
def getBlockCount():
    
    query = ("select count(*) from bitland.block b where id > 0")
    block_count = executeSql(query)[0]
    return block_count


def queryGetPrevBlock():
    
    query = ("select header_hash, id " 
                              + "from bitland.block b "
                              + "join bitland.max_block mb on b.id = mb.max_block" ) 
    prev_block = executeSql(query)[0]
    
    return prev_block 


def queryGetPrevBitcoinBlock():
    
    query = ("select bitcoin_block_height , id " 
                              + "from bitland.block b "
                              + "join bitland.max_block mb on b.id = mb.max_block" ) 
    prev_block = executeSql(query)[0]
    
    return prev_block 


def getOutputParcelByTransactionVout (transaction_hash = '', vout = 0, id = 0):
    
    transaction_hash = str(transaction_hash)
    vout = str(vout)
    id = str(id)
    
    query = ("select planet_id, st_astext(geom) as shape, pub_key, id, vout, transaction_hash, transaction_id, block_id, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address, bitcoin_block_height, miner_bitcoin_address, miner_landbase_address, output_version, transfer_fee_failover_address, claim_fee_sats, claim_block_height, miner_fee_status, transfer_fee_status, miner_fee_status_block_height, transfer_fee_status_block_height " +
             "from bitland.utxo " +
             "where (transaction_hash = '" + transaction_hash + "'" +
             "  and vout = " + vout + ") or id = " + id
             )
    
    try:
        output_parcel = executeSql(query)
        columns = namedtuple('columns', ['planet_id', 'shape', 'pub_key', 'id', 'vout', 'transaction_hash', 'transaction_id', 'block_id', 'miner_fee_sats', 'miner_fee_blocks', 'transfer_fee_sats', 'transfer_fee_blocks', 'transfer_fee_address', 'bitcoin_block_height', 'miner_bitcoin_address', 'miner_landbase_address', 'output_version', 'transfer_fee_failover_address', 'claim_fee_sats', 'claim_block_height', 'miner_fee_status', 'transfer_fee_status', 'miner_fee_status_block_height', 'transfer_fee_status_block_height'])
        utxo_output = columns(
                        output_parcel[0],
                        output_parcel[1],
                        output_parcel[2],
                        output_parcel[3],
                        output_parcel[4],
                        output_parcel[5],
                        output_parcel[6],
                        output_parcel[7],
                        output_parcel[8],
                        output_parcel[9],
                        output_parcel[10],
                        output_parcel[11],
                        output_parcel[12],
                        output_parcel[13],
                        output_parcel[14],
                        output_parcel[15],
                        output_parcel[16],
                        output_parcel[17],
                        output_parcel[18],
                        output_parcel[19],
                        output_parcel[20],
                        output_parcel[21],
                        output_parcel[22],
                        output_parcel[23]
                        )

    except Exception as error:
        print('no utxo found' + str(error))
        utxo_output = 'no matched utxo'
    
    return utxo_output 


def getTransactionInformation (transaction_hash = '', id = 0):
    
    transaction_hash = str(transaction_hash)
    id = str(id)
    
    query = ("select id, block_id, transaction_hash, version, is_landbase, miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address, bitcoin_block_height, miner_fee_status, transfer_fee_status, miner_fee_status_block_height, transfer_fee_status_block_height, miner_bitcoin_address " +
             "from bitland.transaction_contingency " +
             "where (transaction_hash = '" + transaction_hash + "' or id = " + id +");"
             )
    
    print(query)
    
    try:
        transaction = executeSql(query)
        columns = namedtuple('columns', ['id', 'block_id', 'transaction_hash', 'version', 'is_landbase', 'miner_fee_sats', 'miner_fee_blocks', 'transfer_fee_sats', 'transfer_fee_blocks', 'transfer_fee_address', 'bitcoin_block_height','miner_fee_status', 'transfer_fee_status', 'miner_fee_status_block_height', 'transfer_fee_status_block_height', 'miner_bitcoin_address'])
        utxo_output = columns(
                        transaction[0],
                        transaction[1],
                        transaction[2],
                        transaction[3],
                        transaction[4],
                        transaction[5],
                        transaction[6],
                        transaction[7],
                        transaction[8],
                        transaction[9],
                        transaction[10],
                        transaction[11],
                        transaction[12],
                        transaction[13],
                        transaction[14],
                        transaction[15]
                        )

    except Exception as error:
        print('no utxo found' + str(error))
        utxo_output = 'no matched utxo'
    
    return utxo_output 


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
    
    print(query)
    
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
    
    print(query)
    
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


def getClaimByOutputParcelId(output_parcel_id):

    output_parcel_id = str(output_parcel_id)
    
    query = ("select id from bitland.claim where leading_claim is true and invalidated_claim = false and claimed_output_parcel_id = " + output_parcel_id + ";")
    
    try:
        claim_id = executeSql(query)[0]

    except Exception as error:
        print('no claim found' + str(error))
        claim_id = 'no_claim'
    
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


def queryPolygonEquality(polygon1, polygon2):
    
    polygon1 = str(polygon1)
    polygon2 = str(polygon2)
    
    query = ("select st_equals(" + polygon1 +"," + polygon2 +")")
    equal_polygons = executeSql(query)[0]
    
    return equal_polygons 


def queryPolygonRules(outputs):
    
    valid_polygon_decimals = True
    
    for i in range(0,len(outputs)):
        output_shape = outputs[i][2].decode('utf-8')
        query = "select st_astext(st_geomfromtext('" + output_shape + "',4326),6) = '" + output_shape + "';"
        valid_polygon_decimals = executeSql(query)[0]
        if valid_polygon_decimals == False:
            break
    
    return valid_polygon_decimals


def queryPolygonAreaMeters (polygon):
    
    polygon = str(polygon)
    
    query = ("select st_area(st_geomfromtext('" + polygon +"',4326)::geography)")
    area = executeSql(query)[0]
    
    return area 


def queryUnionPolygonAreaMeters (unioned_polygon):
    
    polygon = str(unioned_polygon)
    
    query = ("select st_area(" + unioned_polygon +"::geography)")
    area = executeSql(query)[0]
    
    return area 

'''
def getParcelByTransaction(transaction_hash, vout):
    
    select = ("select op.* "
    + "\n from bitland.output_parcel op"
    + "\n join bitland.transaction t on op.transaction_id = op.transaction_id"
    + "\n where t.transaction_hash = '" + transaction_hash + "' and op.vout = " + str(vout) + ";")
    
    parcel_info = executeSql(select)
    return parcel_info
'''

def getTransactionIdByHash(transaction_hash):
    
    select = ("select id from bitland.transaction where transaction_hash = '" + transaction_hash + "';")
    
    transaction_id = executeSql(select)
    return transaction_id


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
        
        
def getClaimInformation(claimed_output_parcel_id = 0, claim_action_output_parcel_id = 0):
    claimed_output_parcel_id = str(claimed_output_parcel_id)
    claim_action_output_parcel_id = str(claim_action_output_parcel_id)
    select = ("select id, claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, leading_claim, invalidated_claim, invalidation_input_parcel_id"
              +" from bitland.claim "
              + "where (leading_claim = true and claimed_output_parcel_id = " + claimed_output_parcel_id + ") or claim_action_output_parcel_id = " + claim_action_output_parcel_id + ";")
    
    try:
        claim_sql = executeSql(select)
        columns = namedtuple('columns', ['status', 'id', 'claimed_output_parcel_id', 'claim_action_output_parcel_id', 'claim_fee_sats', 'claim_block_height', 'leading_claim', 'invalidated_claim', 'invalidation_input_parcel_id'])
        claim_output = columns(
                        'identified',
                        claim_sql[0],
                        claim_sql[1],
                        claim_sql[2],
                        claim_sql[3],
                        claim_sql[4],
                        claim_sql[5],
                        claim_sql[6],
                        claim_sql[7]
                        )
        
    except Exception as error:
        #print('no claim found for id' + str(error))
        columns = namedtuple('columns', ['status'])
        claim_output = columns(
                        'unidentified')
        
    return claim_output           
              

def getMedianBlockTime11():
    
    select = ("with max_id as ("
        "\n select max(id) as max_id from bitland.block"
        "\n )"
        "\n select PERCENTILE_CONT(0.5) within group(ORDER BY b.time)"
        "\n from max_id m"
        "\n join bitland.block b on b.id >= (m.max_id - 10)")
    
    median_time_11 = executeSql(select)[0]

    return median_time_11


if __name__ == '__main__':
    
    
    print(getMaxBlock())
    
    print(getPriorBlock())
    
    print(getMedianBlockTime11())
    
    print(getBlockById(1))
    
    utxo = getOutputParcelByTransactionVout('b0bcaa0b93e0802533596449a9efa39f7137895c51baba2fa3eefe38cab8fff6',1)
    
    utxo_id = getOutputParcelByTransactionVout(id=24)
    print(utxo_id)
    
    output_id = 6
    print(getContingencyStatus(output_id))
    
    print(getBlockInformation(block_id = 1))
    print(getBlockInformation(block_header = '00000005ed5cc742c099bda2764b5ce5da88470eaa05c740dcb082f9013344e2'))
    
    print(getBlockHeaders(1,5))
    