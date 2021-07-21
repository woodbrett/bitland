'''
Created on Dec 23, 2020

@author: brett_wood
'''
import threading
import time
from node.blockchain.transaction_operations import validateMempoolTransaction,\
    addTransactionToMempool

transaction_queue = []

def waitInTransactionQueue():
#all processes validating and adding blocks should come through this to avoid conflicting adds

    transaction_queue.append(threading.get_ident())
    print(transaction_queue)
    
    print(threading.get_ident())
    time.sleep(5)
    sleep_time = 0

    while transaction_queue[0] != threading.get_ident():
        time.sleep(1)   
        sleep_time = sleep_time + 1
        print('thread: ' + str(threading.get_ident()) + '; sleep: ' + str(sleep_time))
        if sleep_time > 100:
            return False    
    
    return threading.get_ident()
    

def validateAddTransactionMempool(transaction_bytes, threaded=True):
    
    add_transaction = True
    
    if threaded == True:
        waitInTransactionQueue()
    
    if validateMempoolTransaction(transaction_bytes)[0] == True:
        addTransactionToMempool(transaction_bytes)

    else:
        add_transaction = False
    
    if threaded == True:
        transaction_queue.remove(threading.get_ident())
        print('removed thread')

    return add_transaction    


