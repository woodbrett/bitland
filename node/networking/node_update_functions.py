'''
Created on Jul 12, 2021

@author: brett_wood
'''
import threading
import time
import queue
from binascii import unhexlify, hexlify
from node.networking.peering_functions import messageAllKnownPeers
from node.information.blocks import getMaxBlockHeight
from node.processing.synching import checkPeerBlocks
from node.blockchain.transaction_operations import (
    validateTransaction, 
    addTransactionToMempool,
    validateMempoolTransaction
    )
from node.blockchain.block_adding_queueing import validateAddBlock
from node.blockchain.transaction_adding_queueing import validateAddTransactionMempool

action_queue = []

def queueNewBlockFromPeer(block_height,block,peer='', use_threading=True):

    if use_threading == True:    
        t5 = threading.Thread(target=analyzeNewBlockFromPeer,args=(block_height,block,b'',peer,use_threading),daemon=True)
        t5.start()
        print('thread started, exiting function')
        
    else:
        analyzeNewBlockFromPeer(block_height,block,b'',peer,use_threading)

    return True
    
    
#UPDATE
def analyzeNewBlockFromPeer(block_height,block_hex='',block_bytes=b'',peer='',use_threading=False):
    
    if block_bytes == b'':
        block_bytes = unhexlify(block_hex)
    
    if block_hex == '':
        block_hex = hexlify(block_bytes).decode('utf-8')
    
    print('validating adding block')
    
    add_block = validateAddBlock(block_bytes, block_height, use_threading=use_threading)
    print('successfully added block')
    
    if add_block == True:
        print('sending block to peers')
        sendBlockToPeers(block_height,block_hex,peers_to_exclude=[peer])
    
    return add_block


def sendBlockToPeers(block_height,block,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewBlock'
    payload = {
        "block_height":block_height,
        "block":block
        }
    rest_type = 'put'
    
    send_block = messageAllKnownPeers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude, message_type='send block to peers')    
    
    return send_block


def queueNewTransactionFromPeer(transaction_hex,use_threading=True,peer=''):
    
    if use_threading == True:
        t4 = threading.Thread(target=analyzeNewTransactionFromPeer,args=(transaction_hex,peer,use_threading,),daemon=True)
        t4.start()
        #t4.join() this t4.join may cause circular logic

    else:
        analyzeNewTransactionFromPeer(transaction_hex,peer,use_threading)

    return None


def analyzeNewTransactionFromPeer(transaction_hex,peer='',use_threading=True):
    
    transaction_bytes = unhexlify(transaction_hex)
    
    validate_transaction = validateAddTransactionMempool(transaction_bytes, use_threading)
    
    if validate_transaction == True:
        sendTransactionToPeers(transaction_hex,peers_to_exclude=[peer])

    return validate_transaction


def sendTransactionToPeers(transaction,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewTransaction'
    payload = {
        "transaction":transaction
        }
    rest_type = 'put'
    
    send_transaction = messageAllKnownPeers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude, message_type='send transaction to peers')    
    
    return send_transaction 


if __name__ == '__main__':

    '''
    block = '000100000003a09e9a6d785fff0afbe74ce4546cd344f109883493b84014032e9a7181efd66d1754361d3aaa4175a2a6fe9c884fce3347469b34eff28988ae4598e20060f219211d0ffff0000a8c783331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638071125910001000100010061504f4c59474f4e28282d37352e393337352038312e343531382c2d37352e393337352038312e323939372c2d37372e33343337352038312e323939372c2d37372e33343337352038312e343531382c2d37352e393337352038312e34353138292940bb06c7262838a7a800e425cfe83b25bb9cf98ef14a1443d5550a874400e5652710f4ee6852df1e0d5ec850d1073d65ca27b861e401884d1f3199ca37479d41030000000000000000000000000000000000'
    print(sendBlockToPeers(block))
    '''
    
    block_hex = '000100000006ade0c1c20bb1eca7dc15dac93d293bc1c4588634ce4ffb13f141feb5f5b5e4064c625dfba04e5d610eeb04a71fbeea69cf5f2c8bf574b45d1940901800613f78901d0ffff000000000000000000008c622f848e7534ae6b5688b1273d1d12892fd2130efbd000aafcba8ad6daa4579b41cc8745e2173f44b727e58d1bdd092426c6b9e500f48b3a111002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b7773000000000000053e6112000100010001004e504f4c59474f4e282833332e37352038392e333638322c33332e37352038392e313436382c32322e352038392e313436382c32322e352038392e333638322c33332e37352038392e333638322929401e5e045cd802e80d33bacb258c44a67dcc377bf8fcc1136d7fe88502f0db603dd4dee80d867fa7736dc248ac353648ca18bb94449e0bc0dc65c350024fbc35750000000000000000000000000000000000'    
    block_bytes = unhexlify(block_hex)
    
    #x = analyzeNewBlockFromPeer(88, block_bytes=block_bytes)
    #x = analyzeNewBlockFromPeer(88, block_hex=block_hex)
    #x = queueNewBlockFromPeer(781, block=block_hex, use_threading=False)

    x = validateAddBlock(block_bytes, block_height=781, use_threading=True, realtime_validation=False)



