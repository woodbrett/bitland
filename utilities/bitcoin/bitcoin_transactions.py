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
from utilities.bitcoin.bitcoin_requests import getOutputListBlock,\
    getBlockHashFromHeight, getCurrentBitcoinBlockHeight

#UPDATE add in transaction id
def spendByAddressBitcoinBlock(output_list, bitcoin_height, insert_into_db=False):
    
    insert_statement = "insert into bitcoin.recent_transactions( bitcoin_block_height, address, value, txid ) values " 
    
    counter = 0
    for i in range(0, len(output_list)):
        txid = output_list[i][0]
        address = output_list[i][1]
        value = output_list[i][2]
        
        if counter == 0:
            insert_statement = insert_statement + "(" + str(bitcoin_height) + "," + "'" + address + "'," + str(value) + ",'" + txid + "') "
        else:
            insert_statement = insert_statement + ",(" + str(bitcoin_height) + "," + "'" + address + "'," + str(value) + ",'" + txid + "') "
        
        counter = counter + 1

    if insert_into_db == True and counter > 0:   
        insertBitcoinTransactionDb(insert_statement)
    
    return len(output_list)


def processBitcoinBlock(block_height):
    
    #have had some problems with fetching the block, so have it try maximum of 5 times
    added_block = False
    i = 0
    
    while added_block == False and i < 5:
    
        try: 
            output_list = getOutputListBlock(block_height)
        
            #add the indexed transactions for the block
            spendByAddressBitcoinBlock(output_list, block_height, insert_into_db=True)
            
            #update the block table keeping track of which blocks have been added
            block_hash = getBlockHashFromHeight(block_height)
            insertBitcoinBlockDb(block_height, block_hash)
        
            added_block = True
        
        except:
            
            i = i + 1
    
    if added_block == True:
        return block_height
    
    else:
        return 'failed to add block'


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
    
    node_max_height = getCurrentBitcoinBlockHeight()
    
    if block_height == 0:
        node_block_height = node_max_height
    elif block_height > node_max_height:
        node_block_height = node_max_height
    else:
        node_block_height = block_height

    node_block_hash = getBlockHashFromHeight(node_block_height)
    
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
            
            block_info_last_block = getBlockInformationNodeDb(getMaxBitcoinBlock()) #or 0
            
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
        print('adding bitcoin block ' + str(i + start_bitcoin_height))
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
    
    txid = '6a2d1d183a64ba842f957514936c05290c5be82739154ea6341d57710f52caf3'
    x = realtimeSynchWithBitcoin()
        
