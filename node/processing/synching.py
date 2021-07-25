'''
Created on Jul 14, 2021

@author: brett_wood
'''
from node.information.blocks import (
    getBlocks,
    getMaxBlockHeight,
    getBlockInformation
    )
from node.blockchain.block_serialization import deserialize_block
from binascii import unhexlify,hexlify
from node.networking.node_query_functions import get_blocks_start_end
import json
from node.networking.peering_functions import (
    message_all_connected_peers,
    message_peer
    )
from node.blockchain.block_serialization import deserialize_block
from node.blockchain.validate_block import (
    validateBlock,
    validateBlockHeader
    )
from utilities.hashing import calculateHeaderHashFromBlock
import time
import threading
from node.blockchain.block_adding_queueing import processPeerBlocks
from node.blockchain.mempool_operations import garbageCollectMempool

def start_node(threading=True):
    
    pingPeers()
    #findPeers()
    check_peer_blocks(threading=threading)
    garbageCollectMempool()
    
    t3 = threading.Thread(target=run_node,daemon=True)
    t3.start()
    
    return True


def run_node():
    
    while True:
        time.sleep(60)
        check_peer_blocks()
        print('checking peer blocks')


def pingPeers():

    ping = message_all_connected_peers('/peer/node_queries/getBlockHeight', rest_type='get')
    
    return True
    

def check_peer_blocks(threading=True):
    
    peer_heights = ask_peers_for_height()
    self_height = getMaxBlockHeight()
    max_height = self_height
    max_height_peer = 'self'
    blocks_added = 0
    blocks_removed = 0
    
    print(peer_heights)
    
    for i in range(0,len(peer_heights)):
        
        #UPDATE handle the errors from peers more elegantly
        if peer_heights[i][1] == 'error calling peer':
            None
        
        elif peer_heights[i][1].get('block_height') > max_height:
            max_height= peer_heights[i][1].get('block_height')
            max_height_peer = peer_heights[i][0]
    
    if max_height_peer != 'self':
        #UPDATE to only ask for max of X blocks, 50?
        new_blocks = ask_peer_for_blocks(max_height_peer, max(self_height - 5,1), min(max_height-self_height,50)+self_height)
        
        if threading==True:
            t1 = threading.Thread(target=processPeerBlocks,args=(new_blocks,),daemon=True)
            t1.start()
            t1.join()
        else:
            processPeerBlocks(new_blocks,threading=threading)
            

    return True


def ask_peers_for_height():
    
    heights = message_all_connected_peers('/peer/node_queries/getBlockHeight', rest_type='get')
    
    return heights


#UPDATE
def ask_peer_for_blocks(peer, start_block, end_block):
    
    url = '/peer/node_queries/getBlocks/' + str(start_block) + '/' + str(end_block)
    
    blocks = message_peer(url, peer, rest_type='get')
    
    print(blocks)
    
    return blocks


if __name__ == '__main__':
    
    x = start_node(threading=False)
    
