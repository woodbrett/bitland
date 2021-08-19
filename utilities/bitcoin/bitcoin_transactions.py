'''
Created on Aug 5, 2021

@author: brett_wood
'''
from binascii import unhexlify, hexlify
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from utilities.sql_utils import *
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

    if insert_into_db == True and counter > 0:   
        insertBitcoinTransactionDb(insert_statement)
    
    return len(address_value_array)


def processBitcoinBlock(block_height):
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    block_hash = rpc_connection.getblockhash(block_height)
    block = rpc_connection.getblock(block_hash,2)  
    
    #add the indexed transactions for the block
    spendByAddressBitcoinBlock(block, block_height, insert_into_db=True)
    
    #update the block table keeping track of which blocks have been added
    insertBitcoinBlockDb(block_height, block_hash)
    
    return block_height


def processBitcoinBlocks(start_block_height, end_block_height):
    
    for i in range(0, end_block_height - start_block_height + 1):
        processBitcoinBlock(start_block_height + i)
        print('adding bitcoin block ' + str(start_block_height + i))


def deleteBitcoinBlock(block_height=0,block_hash=''):
    
    block_height = str(block_height)
    
    delete_sql = "select bitcoin.delete_bitcoin_block (" + block_height + ",'" + block_hash + "');"
    
    delete = executeSqlDeleteUpdate(delete_sql)
    
    return None


def getBlockInformationNodeDb(block_height=0):

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    node_max_height = rpc_connection.getblockcount()
    
    if block_height == 0:
        node_block_height = node_max_height
    elif block_height > node_max_height:
        node_block_height = node_max_height
    else:
        node_block_height = block_height

    node_block_hash = rpc_connection.getblockhash(node_block_height)
    
    if block_height == 0:
        db_block_height = getMaxBitcoinBlock()
    else:
        db_block_height = block_height
        
    db_block_hash = getBitcoinBlockHash(db_block_height)
    
    equal_heights = node_block_height == db_block_height
    equal_hashes = node_block_hash == db_block_hash    
    
    return {
        'equal_heights': equal_heights,
        'node_block_height': node_block_height,
        'db_block_height': db_block_height,
        'equal_hashes': equal_hashes,
        'node_block_hash': node_block_hash,
        'db_block_hash': db_block_hash
        }


def rollbackBitcoinBlocksDb():

    max_bitcoin_block_db = getMaxBitcoinBlock()
    equal_heads = getBlockInformationNodeDb(max_bitcoin_block_db).get('equal_hashes')
    
    while equal_heads == False:
        print('rolling back bitcoin block ' + str(max_bitcoin_block_db))
        deleteBitcoinBlock(block_height=max_bitcoin_block_db)
        max_bitcoin_block_db = getMaxBitcoinBlock()
        equal_heads = getBlockInformationNodeDb(max_bitcoin_block_db).get('equal_hashes')
        
    return max_bitcoin_block_db


def realtimeSynchWithBitcoin():
    
    synched = False

    #UPDATE to do rollbacks in bitland blocks in case bitcoin has a chain rollback
    while synched == False:
        
        block_info = getBlockInformationNodeDb()
        
        if block_info.get('equal_heights') == True and block_info.get('equal_hashes') == True:
            synched = True
        
        #UPDATE to ensure they start at same hash
        elif block_info.get('node_block_height') > block_info.get('db_block_height'):
            
            block_info_last_block = getBlockInformationNodeDb(getMaxBitcoinBlock())
            
            if block_info_last_block.get('equal_heights') == True and block_info_last_block.get('equal_hashes') == True:
                processBitcoinBlocks(block_info.get('db_block_height') + 1, block_info.get('node_block_height'))
                #add the new blocks since they are starting from same point
                
            elif block_info_last_block.get('equal_heights') == True and block_info_last_block.get('equal_hashes') == False:
                rollbackBitcoinBlocksDb()
                
        elif block_info.get('equal_heights') == True and block_info.get('equal_hashes') == False:
            rollbackBitcoinBlocksDb()
            
        elif block_info.get('node_block_height') < block_info.get('db_block_height'):
            rollbackBitcoinBlocksDb()
                        
        else:
            break
    
    return synched


def synchWithBitcoin(start_bitcoin_height=0,end_bitcoin_height=0):

    blocks = getBitcoinTransactionBlocks(start_bitcoin_height, end_bitcoin_height)
    print(blocks)
    block_heights = []
    for i in range(0,len(blocks)):
        block_heights.append(blocks[i][0])
    
    print(block_heights)    
    
    for i in range(start_bitcoin_height,end_bitcoin_height+1):
        if i not in block_heights:
            processBitcoinBlock(i)
        
    return True
     
     
#QUERIES
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


def getBitcoinTransactionBlocks(start_block_height, end_block_height):
    
    start_block_height = str(start_block_height)
    end_block_height = str(end_block_height)
    
    query = ("select block_height,block_hash from bitcoin.block where block_height >= " + start_block_height + " and block_height <= " + end_block_height + ";"
            )
        
    blocks = executeSqlMultipleRows(query)
    
    return blocks


def countTransactionBlocks(prior_block_height, block_height):
    
    prior_block_height = str(prior_block_height)
    block_height = str(block_height)
    
    query = ("select count(*) as block_count from bitcoin.block where block_height > " + prior_block_height + " and block_height <= " + block_height + ";"
            )
    
    count = executeSql(query)[0]
    
    return count


def insertBitcoinTransactionDb(insert_query):
        
    query = (insert_query +
            " RETURNING 1;"
            )
    
    insert = executeSql(query)
    
    return None


def insertBitcoinBlockDb(block_height, block_hash):
    
    block_height = str(block_height)
        
    query = ("insert into bitcoin.block values (" + block_height + ", '" + block_hash + "') RETURNING 1;"
            )
    
    insert = executeSql(query)
    
    return None


def getMaxBitcoinBlock():

    query = ("select max(block_height) from bitcoin.block;"
            )
    
    max_block = executeSql(query)[0]
    
    return max_block    


def getBitcoinBlockHash(block_height):
    
    block_height = str(block_height)
    
    query = ("select block_hash from bitcoin.block where block_height = " + block_height + ";"
            )
    
    try:
        block_hash = executeSql(query)[0]
    
    except:
        block_hash = None
    
    return block_hash      
    
    
if __name__ == '__main__':
    
    '''
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
        
    print(getBitcoinTransactionBlocks(5,15))
    print(getBitcoinTransactionBlocks(695216,695225))
    x = synchWithBitcoin(start_bitcoin_height=695216,end_bitcoin_height=695225,synch_last_10=False)
    '''
    
    print(realtimeSynchWithBitcoin())