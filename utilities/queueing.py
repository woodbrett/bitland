'''
Created on Dec 27, 2021

@author: postgres
'''
import threading
import time
import uuid

global block_queue 
global transaction_queue

block_queue = []
transaction_queue = []

def addToQueue(use_queue=True, queue_type='block_queue', function_type=None, id=None):
    
    if use_queue == False:
        return 0
    
    else:        
        if id == None:
            id = uuid.uuid1()
        
        if queue_type == 'block_queue':
            block_queue.append(id)
            print(block_queue)
            print(id)
            sleep_time = 0
        
            while block_queue[0] != id:
                time.sleep(1)   
                sleep_time = sleep_time + 1
                print('thread: ' + str(id) + '; type: ' + str(function_type) + '; sleep: ' + str(sleep_time))
                if sleep_time > 100:
                    raise Exception("Timed out in queue, function type of: " + str(function_type))  
        
        elif queue_type == 'transaction_queue':
            transaction_queue.append(id)
            print(transaction_queue)
            print(id)
            sleep_time = 0
        
            while transaction_queue[0] != id:
                time.sleep(1)   
                sleep_time = sleep_time + 1
                print('thread: ' + str(id) + '; type: ' + str(function_type) + '; sleep: ' + str(sleep_time))
                if sleep_time > 100:
                    raise Exception("Timed out in queue, function type of: " + str(function_type))  
        
        else:
            raise Exception("Invalid queue type for adding to queue")
            
        return id


def removeFromQueue(use_queue=True,queue_type='block_queue',id=None):
    
    if use_queue == False:
        return id
    
    else:
        if queue_type == 'block_queue':
            if id in block_queue:
                block_queue.remove(id)
                return id
            else:
                raise Exception("Queue id not present in queue")
        if queue_type == 'transaction_queue':
            if id in transaction_queue:
                transaction_queue.remove(id)
                return id
            else:
                raise Exception("Queue id not present in queue")
        else:
            raise Exception("Invalid queue type for removing from queue")


def viewQueue(queue_type='block_queue'):
    
    return block_queue


