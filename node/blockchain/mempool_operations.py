'''
Created on Jul 20, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSql

def garbageCollectMempool():
    
    return True


def removeTransactionsFromMempool(block_id):
    
    query = ("delete from bitland.transaction_mempool " +
                "where id in (" +
                "select m.id " +
                "from bitland.transaction t " +
                "join bitland.transaction_mempool m on t.transaction_hash = m.transaction_hash and t.block_id = " +str(block_id) + ");"
                )

    print(query)

    try:
        delete = executeSql(query)
        
    except Exception as error:
        #print('error deleting mempool transactions' )
        delete = 'none deleted'
    
    return delete


