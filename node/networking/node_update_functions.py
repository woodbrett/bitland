'''
Created on Jul 12, 2021

@author: brett_wood
'''
import threading
import time
import queue
from binascii import unhexlify
from node.networking.peering_functions import message_all_connected_peers
from node.information.blocks import getMaxBlockHeight
from node.processing.synching import check_peer_blocks
from node.blockchain.transaction_operations import (
    validateTransaction, 
    addTransactionToMempool,
    validateMempoolTransaction
    )
from node.blockchain.block_adding_queueing import validateAddBlock

action_queue = []

def queue_new_block_from_peer(block_height,block,peer=''):
    
    t1 = threading.Thread(target=analyze_new_block_from_peer,args=(block_height,block,peer,),daemon=True)
    t1.start()

    print('thread started, exiting function')

    return True
    

#UPDATE
def analyze_new_block_from_peer(block_height,block,peer=''):
    
    block_bytes = unhexlify(block)
    add_block = validateAddBlock(block_bytes, block_height)
    
    if add_block == True:
        send_block_to_peers(block_height,block,peers_to_exclude=[peer])
    
    return add_block


def send_block_to_peers(block_height,block,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewBlock'
    payload = {
        "block_height":block_height,
        "block":block
        }
    rest_type = 'put'
    
    send_block = message_all_connected_peers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
    return send_block


def queue_new_transaction_from_peer(transaction,peer=''):
    
    t1 = threading.Thread(target=analyze_new_transaction_from_peer,args=(transaction,peer,),daemon=True)
    t1.start()

    print('thread started, exiting function')

    return True


def analyze_new_transaction_from_peer(transaction,peer=''):
    
    action_queue.append(threading.get_ident())
    time.sleep(5)

    while action_queue[0] != threading.get_ident():
        time.sleep(1)
        print('a')
    
    transaction_bytes = unhexlify(transaction)
    print(transaction_bytes)

    if validateMempoolTransaction(transaction_bytes)[0] == True:
        addTransactionToMempool(transaction_bytes)
        send_transaction_to_peers(transaction,peers_to_exclude=[peer])
        
    else:
        return False
        
    action_queue.remove(threading.get_ident())

    return True


def send_transaction_to_peers(transaction,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewTransaction'
    payload = {
        "transaction":transaction
        }
    rest_type = 'put'
    
    send_transaction = message_all_connected_peers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
    return send_transaction 


if __name__ == '__main__':

    '''
    block = '000100000003a09e9a6d785fff0afbe74ce4546cd344f109883493b84014032e9a7181efd66d1754361d3aaa4175a2a6fe9c884fce3347469b34eff28988ae4598e20060f219211d0ffff0000a8c783331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638071125910001000100010061504f4c59474f4e28282d37352e393337352038312e343531382c2d37352e393337352038312e323939372c2d37372e33343337352038312e323939372c2d37372e33343337352038312e343531382c2d37352e393337352038312e34353138292940bb06c7262838a7a800e425cfe83b25bb9cf98ef14a1443d5550a874400e5652710f4ee6852df1e0d5ec850d1073d65ca27b861e401884d1f3199ca37479d41030000000000000000000000000000000000'
    print(send_block_to_peers(block))
    '''
    
    transaction = '000201013c75b4c2a69b3a86e13ac62705a6cf2d8a56d7d8b8d18bf846c621d62478fe060040ebff9ba202e4e182ed5d5fd685e4220279547ce2368f93a9453174def02b454d9c93667c18e65ed24968b181be63a38af117a3c0c5b59e7e94baf8c5b602f7d70101010054504f4c59474f4e28282d33392e3337352038372e373637312c2d33392e3337352038372e36323530382c2d34352038372e36323530382c2d34352038372e373637312c2d33392e3337352038372e37363731292940e3f2ecdefaa8e3f6652e8960dcca0d09d713fe255cbb5920c79e5dfe46f9447971cb2c76c7e6870ec9641924fa7a4ce7955bf911caf8be624cb21e4cfbcbfaf30000000000000000000000000000000000'
    #x = queue_new_transaction_from_peer(transaction)
    x = analyze_new_transaction_from_peer(transaction)
    print(x)
    
    