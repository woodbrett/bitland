'''
Created on Jul 20, 2021

@author: brett_wood
'''
from utilities.sqlUtils import executeSqlDeleteUpdate

def garbageCollectMempool():
    
    query = ("delete from bitland.transaction_mempool " +
                "where id in (" +
                "select m.id " +
                "from bitland.transaction t " +
                "join bitland.transaction_mempool m on t.transaction_hash = m.transaction_hash );"
                )

    try:
        delete = executeSqlDeleteUpdate(query)
        
    except Exception as error:
        #print('error deleting mempool transactions' )
        delete = 'none deleted'
    
    return delete


def removeTransactionsFromMempool(block_id):
    
    query = ("delete from bitland.transaction_mempool " +
                "where id in (" +
                "select m.id " +
                "from bitland.transaction t " +
                "join bitland.transaction_mempool m on t.transaction_hash = m.transaction_hash and t.block_id = " +str(block_id) + ");"
                )

    try:
        delete = executeSqlDeleteUpdate(query)
        
    except Exception as error:
        #print('error deleting mempool transactions' )
        delete = 'none deleted'
    
    return delete


if __name__ == '__main__':

    print(garbageCollectMempool())

