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

def queueNewBlockFromPeer(block_height,block,peer=''):
    
    t3 = threading.Thread(target=analyzeNewBlockFromPeer,args=(block_height,block,b'',peer,),daemon=True)
    t3.start()

    #analyzeNewBlockFromPeer(block_height,block,b'',peer)

    print('thread started, exiting function')

    return True
    
    
#UPDATE
def analyzeNewBlockFromPeer(block_height,block_hex='',block_bytes=b'',peer=''):
    
    if block_bytes == b'':
        block_bytes = unhexlify(block_hex)
    
    if block_hex == '':
        block_hex = hexlify(block_bytes).decode('utf-8')
    
    add_block = validateAddBlock(block_bytes, block_height)
    
    if add_block == True:
        sendBlockToPeers(block_height,block_hex,peers_to_exclude=[peer])
    
    return add_block


def sendBlockToPeers(block_height,block,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewBlock'
    payload = {
        "block_height":block_height,
        "block":block
        }
    rest_type = 'put'
    
    send_block = messageAllKnownPeers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
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
    
    send_transaction = messageAllKnownPeers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
    return send_transaction 


if __name__ == '__main__':

    '''
    block = '000100000003a09e9a6d785fff0afbe74ce4546cd344f109883493b84014032e9a7181efd66d1754361d3aaa4175a2a6fe9c884fce3347469b34eff28988ae4598e20060f219211d0ffff0000a8c783331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638071125910001000100010061504f4c59474f4e28282d37352e393337352038312e343531382c2d37352e393337352038312e323939372c2d37372e33343337352038312e323939372c2d37372e33343337352038312e343531382c2d37352e393337352038312e34353138292940bb06c7262838a7a800e425cfe83b25bb9cf98ef14a1443d5550a874400e5652710f4ee6852df1e0d5ec850d1073d65ca27b861e401884d1f3199ca37479d41030000000000000000000000000000000000'
    print(sendBlockToPeers(block))
    '''
    
    block_hex = '0001000000053da2d5864104aba5adba744024e319b9a83fd5328522fe72e561cd991e711654dd173773c735ae568f61ffab270e8520a8dc7301188d18421d1672140061203da01d0ffff000000000000000000004952c2042810823b45ce37c617f20222f01cf1b922103000aa19f012bfa333fc8940af142896ef9c940dee61bd9af7b0d707a3998a18a5f7079ff002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b77730000000000000b0654220001000100010066504f4c59474f4e28282d38332e3637313837352037382e34343534342c2d38332e3637313837352037382e323139392c2d38342e3337352037382e323139392c2d38342e3337352037382e34343534342c2d38332e3637313837352037382e3434353434292940d0134626df0ad197078050a7b016eac3d6b2fa27fa3c3d7aa0dbf37472ffccd9edb8ea100f34bff4906e6e10e4970db06799d3d40815acb7640040af37d1ca7f0000000000000000000000000000000000'    
    block_bytes = unhexlify(block_hex)
    
    #x = analyzeNewBlockFromPeer(88, block_bytes=block_bytes)
    #x = analyzeNewBlockFromPeer(88, block_hex=block_hex)
    x = queueNewBlockFromPeer(88, block=block_hex)
