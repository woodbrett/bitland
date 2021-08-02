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
from node.blockchain.transaction_adding_queueing import validateAddTransactionMempool

action_queue = []

def queue_new_block_from_peer(block_height,block,peer=''):
    
    t3 = threading.Thread(target=analyze_new_block_from_peer,args=(block_height,block,peer,),daemon=True)
    t3.start()

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


def queue_new_transaction_from_peer(transaction_hex,use_threading=True,peer=''):
    
    print('new transaction queued, peers',flush=True)
    print(peer)
    
    if use_threading == True:
        t4 = threading.Thread(target=analyze_new_transaction_from_peer,args=(transaction_hex,peer,use_threading,),daemon=True)
        t4.start()
        #t4.join()

    else:
        analyze_new_transaction_from_peer(transaction_hex,peer,use_threading)

    return None


def analyze_new_transaction_from_peer(transaction_hex,peer='',use_threading=True):
    
    transaction_bytes = unhexlify(transaction_hex)
    
    print('analyzing new transaction')
    print(peer)
    
    validate_transaction = validateAddTransactionMempool(transaction_bytes, use_threading)

    if validate_transaction == True:
        print('sending transaction to peers')
        send_transaction_to_peers(transaction_hex,peers_to_exclude=[peer])

    return validate_transaction


def send_transaction_to_peers(transaction,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewTransaction'
    payload = {
        "transaction":transaction
        }
    rest_type = 'put'
    
    print('sending_transaction to peers 2, peers to exclude', flush=True)
    print(peers_to_exclude,flush=True)
    
    send_transaction = message_all_connected_peers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
    return send_transaction 


if __name__ == '__main__':

    '''
    block = '000100000003a09e9a6d785fff0afbe74ce4546cd344f109883493b84014032e9a7181efd66d1754361d3aaa4175a2a6fe9c884fce3347469b34eff28988ae4598e20060f219211d0ffff0000a8c783331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638071125910001000100010061504f4c59474f4e28282d37352e393337352038312e343531382c2d37352e393337352038312e323939372c2d37372e33343337352038312e323939372c2d37372e33343337352038312e343531382c2d37352e393337352038312e34353138292940bb06c7262838a7a800e425cfe83b25bb9cf98ef14a1443d5550a874400e5652710f4ee6852df1e0d5ec850d1073d65ca27b861e401884d1f3199ca37479d41030000000000000000000000000000000000'
    print(send_block_to_peers(block))
    '''
    
    transaction_hex = '0002010103aca220f7ec55e458acd9aafadc9af571da0676846fb6d5e2505c82a8849782004078708125ab06305a739e7ac4dbc7f0a3a571aad4976369069cf27469262b6f8650d0b508b73e36953f3b59934abc2ddad4ef5442114bae127d9efc49ba8810080101010051504f4c59474f4e28282d32322e352038392e37343637342c2d32322e352038392e35313836382c2d34352038392e35313836382c2d34352038392e37343637342c2d32322e352038392e373436373429294069022ccf1a0644a5e07eb2f89b3e9ab217fcc158f3525655a2a30f66c0c61a916858846f55db7172d5e71e3399d18fc191f0efc9b1fa12efcaeab17e0bbe27db0000000000000000000000000000000000'    
    
    x = queue_new_transaction_from_peer(transaction_hex, use_threading=False)
    
    