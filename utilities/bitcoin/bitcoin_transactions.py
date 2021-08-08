'''
Created on Aug 5, 2021

@author: brett_wood
'''
from binascii import unhexlify, hexlify
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from utilities.sqlUtils import *
from system_variables import (
    rpc_user,
    rpc_password,
    node_url 
    )


#UPDATE add in transaction id
def spendByAddressBitcoinBlock(bitcoin_block, bitcoin_height, insert_into_db=False):
    
    transactions = bitcoin_block.get('tx')
    address_value_array = []
    insert_statement = "insert into bitcoin.recent_transactions( bitcoin_block_height, address, value, txid ) values " 
    
    counter = 0
    for i in range(0,len(transactions)):
        transaction_vout = transactions[i].get('vout')
        txid = transactions[i].get('txid')
        for j in range(0,len(transaction_vout)):
            value = transaction_vout[j].get('value') * 100000000
            addresses = transaction_vout[j].get('scriptPubKey').get('addresses')
            if addresses != None and len(addresses) == 1:
                address = addresses[0]
                address_value_array.append([address,value])
                if counter == 0:
                    insert_statement = insert_statement + "(" + str(bitcoin_height) + "," + "'" + address + "'," + str(value) + ",'" + txid + "') "
                else:
                    insert_statement = insert_statement + ",(" + str(bitcoin_height) + "," + "'" + address + "'," + str(value) + ",'" + txid + "') "
                
                counter = counter + 1

    if insert_into_db == True:   
        insertBitcoinTransactionDb(insert_statement)
    
    return len(address_value_array)


def insertBitcoinTransactionDb(insert_query):
        
    query = (insert_query +
            " RETURNING 1;"
            )
    
    insert = executeSql(query)
    
    return None


def processBitcoinBlock(block_height):
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    block_hash = rpc_connection.getblockhash(block_height)
    block = rpc_connection.getblock(block_hash,2)  
    
    spendByAddressBitcoinBlock(block, block_height, insert_into_db=True)
    
    return block_height


def countTransactionBlocks(prior_block_height, block_height):
    
    prior_block_height = str(prior_block_height)
    block_height = str(block_height)
    
    query = ("select count(*) as block_count from bitcoin.transaction_blocks where bitcoin_block_height > " + prior_block_height + " and bitcoin_block_height <= " + block_height + ";"
            )
    
    count = executeSql(query)[0]
    
    return count


def insertRelevantTransactions(prior_bitcoin_block_height, bitcoin_block_height, bitland_block_height):
    
    prior_bitcoin_block_height = str(prior_bitcoin_block_height)
    bitcoin_block_height = str(bitcoin_block_height)
    bitland_block_height = str(bitland_block_height)

    query = (    
        "insert into bitcoin.relevant_contingency_transaction " +
        " select distinct t.bitcoin_block_height, t.address, t.value, t.txid, " + bitland_block_height +
        " from bitland.vw_contingency_status c " +
        " join bitcoin.recent_transactions t on c.bitcoin_address = t.address " +
        "  and t.value = fee_sats " +
        "  and t.bitcoin_block_height > " + prior_bitcoin_block_height + 
        "  and t.bitcoin_block_height <= " + bitcoin_block_height +
        "  and validation_bitcoin_block_height is null returning 1; "
        )
    
    insert_count = executeSqlInsert(query)
    
    return insert_count
    
    
if __name__ == '__main__':

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    #best_block_hash = rpc_connection.getbestblockhash()
    block_hash = rpc_connection.getblockhash(693841)
    block = rpc_connection.getblock(block_hash,2)
    #print(block)

    txs = block.get('tx')
    #print(txs)
    print(txs[1].get('vout'))
    print(txs[1].get('txid'))
    print(txs[1].get('vout')[0].get('value'))

    #print(len(spendByAddressBitcoinBlock(block)))
    
    for i in range(693844,694501):
        print(processBitcoinBlock(i))
    
    #print(countTransactionBlocks(693908, 693915))
    
    #print(insertRelevantTransactions(693908, 693915, 230))
    