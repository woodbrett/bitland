'''
Created on Dec 23, 2020

@author: brett_wood
'''
import threading
import time
from node.blockchain.transaction_operations import validateMempoolTransaction,\
    addTransactionToMempool
from utilities.queueing import addToQueue, removeFromQueue

def validateAddTransactionMempool(transaction_bytes, use_queue=True):
    
    queue_id = addToQueue(use_queue=use_queue, queue_type='transaction_queue', function_type='add transaction to mempool')
    
    try:
        if validateMempoolTransaction(transaction_bytes)[0] == True:
            addTransactionToMempool(transaction_bytes)

        else:
            add_transaction = False
            
    except:
        print('error adding transaction to mempool')
        add_transaction = False
    
    removeFromQueue(use_queue=use_queue,queue_type='transaction_queue',id=queue_id)  
    
    return add_transaction    


