'''
Created on Jul 12, 2021

@author: brett_wood
'''
import threading
import time
import queue
from node.blockchain.validate_block import validateBlock
from node.blockchain.block_operations import addBlock
from binascii import unhexlify
from node.networking.peering_functions import message_all_connected_peers
from node.information.blocks import getMaxBlockHeight
from node.processing.synching import synch_node

action_queue = []

def queue_new_block_from_peer(block_height,block,peer=''):
    
    t1 = threading.Thread(target=analyze_new_block_from_peer,args=(block_height,block,peer,),daemon=True)
    t1.start()

    print('thread started, exiting function')

    return True
    

def analyze_new_block_from_peer(block_height,block,peer):
    
    action_queue.append(threading.get_ident())
    print(action_queue)
    
    print(threading.get_ident())
    time.sleep(5)

    while action_queue[0] != threading.get_ident():
        time.sleep(1)        

    self_height = getMaxBlockHeight()
    block_bytes = unhexlify(block)

    if block_height > self_height + 1:
        synch_node()
    
    elif block_height == self_height + 1:
        if validateBlock(block_bytes) == True:
            addBlock(block_bytes)
            send_block_to_peers(block,peers_to_exclude=[peer])
            
        #UPDATE make sure it didn't not validate because of something wrong, but rather different chain (prior block different)
        else:
            synch_node()
            
        
        
    #UPDATE - put in logic if the block is invalid but ahead of the current block, it should validate if its a valid separate chain and update accordingly
    
    action_queue.remove(threading.get_ident())


#UPDATE - send block to peers when its validated and added, don't send it back to peer who you received it from
def send_block_to_peers(block,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewBlock'
    payload = {"block":block}
    rest_type = 'put'
    
    send_block = message_all_connected_peers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
    return send_block


if __name__ == '__main__':

    #block = '0001000000072b91bab08c8290d50c6cac2620155c143485765ba9c91593bc62d48f20a8599eb2a32d8c558df5a97c8198043e1b8f3bffbf0293fc45f0762e68692e0060ecd9751d0ffff0000a8a363331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638000016e50001000100010059504f4c59474f4e28282d32382e3132352038382e36393036382c2d32382e3132352038382e3436312c2d33332e37352038382e3436312c2d33332e37352038382e36393036382c2d32382e3132352038382e363930363829294046238ced0d9a9316196ca2bb32cffc70c3ec28f15d0b2fa4c38a592d0424f1cfc67793797bd23629b7ac49783756cc170db2e0393ae1bed6911f4584ecfa654a0000000000000000000000000000000000'
    block = '000100000003a09e9a6d785fff0afbe74ce4546cd344f109883493b84014032e9a7181efd66d1754361d3aaa4175a2a6fe9c884fce3347469b34eff28988ae4598e20060f219211d0ffff0000a8c783331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638071125910001000100010061504f4c59474f4e28282d37352e393337352038312e343531382c2d37352e393337352038312e323939372c2d37372e33343337352038312e323939372c2d37372e33343337352038312e343531382c2d37352e393337352038312e34353138292940bb06c7262838a7a800e425cfe83b25bb9cf98ef14a1443d5550a874400e5652710f4ee6852df1e0d5ec850d1073d65ca27b861e401884d1f3199ca37479d41030000000000000000000000000000000000'
    
    print(send_block_to_peers(block))
    
    '''
    block_bytes = unhexlify(block)
    
    #print(validateBlock(block_bytes))
    
    x = queue_new_block_from_peer(block)
    
    if validateBlock(block_bytes)[0] == True:
        addBlock(block_bytes)    
    
    print(validateBlock(block_bytes))
    '''
    
    
    
    