'''
Created on Jul 14, 2021

@author: brett_wood
'''
from node.information.blocks import (
    getMaxBlockHeight
    )
from node.blockchain.block_serialization import deserializeBlock
from binascii import unhexlify,hexlify
from node.networking.node_query_functions import getBlocksStartEnd
import json
from node.networking.peering_functions import (
    messageAllConnectedPeers,
    messagePeer, updatePeer, connectToPeer, queryPeer,
    attemptToConnectToNewPeer, deletePeer
    )
from node.blockchain.block_serialization import deserializeBlock
from node.blockchain.validate_block import (
    validateBlock,
    validateBlockHeader
    )
from utilities.hashing import calculateHeaderHashFromBlock
import time
import threading
from node.blockchain.block_adding_queueing import processPeerBlocks,\
    synchBitcoin
from node.blockchain.mempool_operations import garbageCollectMempool
from ipaddress import ip_address
from node.blockchain.global_variables import bitland_version
from system_variables import peering_port

def start_node():
    
    pingPeers()
    #findPeers()

    synchBitcoin()
    print('synched bitcoin')
    
    checkPeerBlocks()
    print('checked peers')
    garbageCollectMempool()
    
    return True


def run_node():
    
    while True:
        time.sleep(120)
        
        print('checking peer blocks')
        checkPeerBlocks()
        
        print('synching bitcoin')
        synchBitcoin()


def pingPeers():

    ping = messageAllConnectedPeers('/peer/peering/ping', rest_type='get',peer_types=['connected','unpeered','offline'])
    
    for i in range(0,len(ping)):
        
        ip_address= ping[i][0]
        
        if ping[i][1] == 'error calling peer':
            updatePeer(ip_address=ip_address,status='offline')
        
        elif ping[i][1].get('message') == 'Not authenticated as peer':
            
            peer_port = queryPeer(ip_address=ip_address).get('port')
            deletePeer(ip_address)
            attemptToConnectToNewPeer(bitland_version, peering_port, int(time.time()), ip_address, peer_port)
        
        else:
            updatePeer(ip_address=ping[i][0],status='connected')
    
    return True


def initialSynch():
    
    synched = False
    
    while synched == False:
        synch_peer = checkPeerBlocks(use_threading=False)
        synched = synch_peer.get('peer_height') == synch_peer.get('self_height')
    

def checkPeerBlocks(use_threading=True):
    
    peer_heights = askPeersForHeight()
    self_height = getMaxBlockHeight()
    max_height = self_height
    max_height_peer = 'self'
    blocks_added = 0
    blocks_removed = 0
    
    for i in range(0,len(peer_heights)):
        
        #UPDATE handle the errors from peers more elegantly
        if peer_heights[i][1] == 'error calling peer':
            None
        
        elif peer_heights[i][1].get('block_height') > max_height:
            max_height= peer_heights[i][1].get('block_height')
            max_height_peer = peer_heights[i][0]
    
    if max_height_peer != 'self':
        #UPDATE to only ask for max of X blocks, 50?
        
        synched_with_peers = 'out of synch'
        
        new_blocks = askPeerForBlocks(max_height_peer, max(self_height - 5,0), min(max_height-self_height,50)+self_height)
        
        if use_threading==True:
            t1 = threading.Thread(target=processPeerBlocks,args=(new_blocks,use_threading,),daemon=True)
            t1.start()
            t1.join()
        else:
            processPeerBlocks(new_blocks,use_threading=use_threading)

    return {
        'peer_height': max_height_peer,
        'self_height' getMaxBlockHeight()
        }


def askPeersForHeight():
    
    heights = messageAllConnectedPeers('/peer/node_queries/getBlockHeight', rest_type='get')
    
    return heights


#UPDATE
def askPeerForBlocks(peer, start_block, end_block):
    
    url = '/peer/node_queries/getBlocks/' + str(start_block) + '/' + str(end_block)
    
    blocks = message_peer(url, peer, rest_type='get')
    
    print(blocks)
    
    return blocks


if __name__ == '__main__':
    
    #x = start_node()
    x = checkPeerBlocks(use_threading=False)
