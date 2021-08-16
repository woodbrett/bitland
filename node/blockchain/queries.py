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
def addClaimToDb(claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, status, from_bitland_block_height):

    claimed_output_parcel_id = str(claimed_output_parcel_id)
    claim_action_output_parcel_id = str(claim_action_output_parcel_id)
    claim_fee_sats = str(claim_fee_sats) 
    claim_block_height =  str(claim_block_height)
    from_bitland_block_height =  str(from_bitland_block_height)
    
    query = ("insert into bitland.claim (claimed_output_parcel_id, claim_action_output_parcel_id, claim_fee_sats, claim_block_height, status ,from_bitland_block_height) values " +
            "(" + claimed_output_parcel_id + "," +
            claim_action_output_parcel_id + "," +  
            claim_fee_sats + "," +  
            claim_block_height + "," +  
            "'" + status + "'," +  
            from_bitland_block_height + ") "
            "RETURNING id;"
            )
    
    claim_id = executeSql(query)
    
    return claim_id


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
              



