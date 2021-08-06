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


def spendByAddressBitcoinBlock(bitcoin_block, bitcoin_height, insert_into_db=False):
    
    transactions = bitcoin_block.get('tx')
    address_value_array = []
    insert_statement = "insert into bitcoin.recent_transactions( bitcoin_block_height, address, value ) values " 
    
    counter = 0
    for i in range(0,len(transactions)):
        transaction_vout = transactions[i].get('vout')
        for j in range(0,len(transaction_vout)):
            value = transaction_vout[j].get('value')
            addresses = transaction_vout[j].get('scriptPubKey').get('addresses')
            if addresses != None and len(addresses) == 1:
                address = addresses[0]
                address_value_array.append([address,value])
                if counter == 0:
                    insert_statement = insert_statement + "(" + str(bitcoin_height) + "," + "'" + address + "'," + str(value) + ") "
                else:
                    insert_statement = insert_statement + ",(" + str(bitcoin_height) + "," + "'" + address + "'," + str(value) + ") "
                
                counter = counter + 1

    if insert_into_db == True:   
        insertBitcoinTransactionDb(insert_statement)
    
    return None


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


if __name__ == '__main__':

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    #best_block_hash = rpc_connection.getbestblockhash()
    block_hash = rpc_connection.getblockhash(693843)
    block = rpc_connection.getblock(block_hash,2)
    #print(block)

    #txs = block.get('tx')
    #print(txs)
    #print(txs[0].get('vout'))
    #print(txs[1].get('vout')[0].get('value'))

    #print(len(spendByAddressBitcoinBlock(block)))
    
    for i in range(693844,694345):
        print(processBitcoinBlock(i))
    
    
    
