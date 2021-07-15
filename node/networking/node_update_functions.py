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

action_queue = []

def queue_new_block_from_peer(block,peer=''):
    
    t1 = threading.Thread(target=analyze_new_block_from_peer,args=(block,peer,),daemon=True)
    t1.start()

    print('thread started, exiting function')

    return True
    

def analyze_new_block_from_peer(block,peer):
    
    action_queue.append(threading.get_ident())
    print(action_queue)
    
    print(threading.get_ident())
    time.sleep(5)

    while action_queue[0] != threading.get_ident():
        time.sleep(1)        

    block_bytes = unhexlify(block)

    if validateBlock(block_bytes) == True:
        addBlock(block_bytes)
        send_block_to_peers(block,peers_to_exclude=[peer])
        
    #UPDATE - put in logic if the block is invalid but ahead of the current block, it should validate if its a valid separate chain and update accordingly
    
    action_queue.remove(threading.get_ident())


#UPDATE - send block to peers when its validated and added, don't send it back to peer who you received it from
def send_block_to_peers(block,peers_to_exclude=[]):
    
    endpoint = '/peer/node_updates/sendNewBlock'
    payload = block
    rest_type = 'post'
    
    send_block = message_all_connected_peers(endpoint=endpoint, payload=payload, rest_type=rest_type, peers_to_exclude=peers_to_exclude)    
    
    return send_block


if __name__ == '__main__':

    #block = '0001000000072b91bab08c8290d50c6cac2620155c143485765ba9c91593bc62d48f20a8599eb2a32d8c558df5a97c8198043e1b8f3bffbf0293fc45f0762e68692e0060ecd9751d0ffff0000a8a363331333534653737353536623734356137343334366235373464346337313462333535313463373237383431346435313631373037393635343637383431363933363638000016e50001000100010059504f4c59474f4e28282d32382e3132352038382e36393036382c2d32382e3132352038382e3436312c2d33332e37352038382e3436312c2d33332e37352038382e36393036382c2d32382e3132352038382e363930363829294046238ced0d9a9316196ca2bb32cffc70c3ec28f15d0b2fa4c38a592d0424f1cfc67793797bd23629b7ac49783756cc170db2e0393ae1bed6911f4584ecfa654a0000000000000000000000000000000000'
    block = '0001000000072b91bab08c8290d50c6cac2620155c143485765ba9c91593bc62d48f46da56ee09a208af6badf28fe8a4bdb300c651ab270980c0fe4d7dcb804a57ae0060ecdb271d0ffff0000a8a36333133353465373735353662373435613734333436623537346434633731346233353531346337323738343134643531363137303739363534363738343136393336363800e810c30001000100010059504f4c59474f4e28282d32382e3132352038382e36393036382c2d32382e3132352038382e3436312c2d33332e37352038382e3436312c2d33332e37352038382e36393036382c2d32382e3132352038382e36393036382929404055aba9fdc64318b585a41fe66a1101efeec0d5f7794dea2a55df356e9deea1597c4e00eea023122f98e1c5b9fbea2ee02b19973cd442e10d7dbe526753b2510000000000000000000000000000000000'
    
    print(send_block_to_peers(block))
    
    '''
    block_bytes = unhexlify(block)
    
    #print(validateBlock(block_bytes))
    
    x = queue_new_block_from_peer(block)
    
    if validateBlock(block_bytes)[0] == True:
        addBlock(block_bytes)    
    
    print(validateBlock(block_bytes))
    '''
    
    
    
    