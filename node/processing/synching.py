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
    messageAllKnownPeers,
    messagePeer, updatePeer, initialConnectToPeer, validateConnectToPeer, queryPeer,
    attemptToConnectToNewPeer, deletePeer, peerCount, resetPeers
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
    synchBitcoin, checkPeerBlocks
from node.blockchain.mempool_operations import garbageCollectMempool
from ipaddress import ip_address
from node.blockchain.global_variables import bitland_version
from system_variables import peering_port
from utilities.time_utils import getTimeNowSeconds

def start_node():

    print('resetting peers')
    resetPeers()
    
    print('pinging peers')
    pingPeers()
    
    print('checking peer blocks')
    peer_height = 1
    self_height = 0
    while self_height < peer_height:
        block_comparison = checkPeerBlocks(use_threading=True)
        peer_height = block_comparison.get('peer_height')
        self_height = block_comparison.get('self_height')
        
    #t3 = threading.Thread(target=checkPeerBlocks,args=(True,),daemon=True)
    #t3.start()
        
    print('synching bitcoin')
    synchBitcoin()
    
    return True


def run_node(initial_synch=False):
    
    pingPeers(peer_types=['connected','unpeered'])
    
    if initial_synch == True:
        initialSynch()
    
    while True:
        
        print('checking peer blocks')
        t3 = threading.Thread(target=checkPeerBlocks,args=(True,),daemon=True)
        t3.start()
        
        print('synching bitcoin')
        synchBitcoin()
        
        pingPeers(peer_types=['connected'])
        
        time.sleep(120)


def pingPeers(peer_types=['connected','unpeered','offline',None]):

    ping = messageAllKnownPeers('/peer/peering/ping', rest_type='get',peer_types=['connected','unpeered','offline',None])
    
    for i in range(0,len(ping)):
        
        ip_address= ping[i].get('peer_ip_address')
        port= ping[i].get('peer_port')
        peer_response = ping[i].get('response')
        
        if peer_response == 'error calling peer':
            updatePeer(ip_address=ip_address,port=port,status='offline')
        
        elif peer_response.get('message') == 'Not authenticated as peer':
            
            peer_port = queryPeer(ip_address=ip_address).get('port')
            deletePeer(ip_address,peer_port)
            attemptToConnectToNewPeer(bitland_version, peering_port, getTimeNowSeconds(), ip_address, peer_port)
        
        else:
            updatePeer(ip_address=ip_address,port=port,status='connected')
    
    return True


def initialSynch():
    
    print('performing initial synch')
    
    peer_count = peerCount()
    while peer_count == 0:
        print('peer count 0, waiting')
        time.sleep(10)
        peer_count = peerCount()
    
    synched = False
    while synched == False:
        synch_peer = checkPeerBlocks(use_threading=False)
        synched = synch_peer.get('peer_height') == synch_peer.get('self_height')
    

# def checkPeerBlocks(use_threading=True):
#
#     peer_heights = askPeersForHeight()
#     self_height = getMaxBlockHeight()
#     max_height = self_height
#     max_height_peer = 'self'
#     blocks_added = 0
#     blocks_removed = 0
#
#     for i in range(0,len(peer_heights)):
#
#         peer_response = peer_heights[i].get('response')
#
#         #UPDATE handle the errors from peers more elegantly
#         if peer_response == 'error calling peer':
#             None
#
#         elif peer_response.get('block_height') > max_height:
#             max_height= peer_response.get('block_height')
#             max_height_peer = peer_heights[i].get('peer_ip_address')
#
#     if max_height_peer != 'self':
#         #UPDATE to only ask for max of X blocks, 50?
#
#         synched_with_peers = 'out of synch'
#
#         new_blocks = askPeerForBlocks(max_height_peer, max(self_height - 5,0), min(max_height-self_height,50)+self_height)
#
#         if use_threading==True:
#             t1 = threading.Thread(target=processPeerBlocks,args=(new_blocks,use_threading,),daemon=True)
#             t1.start()
#             t1.join()
#         else:
#             processPeerBlocks(new_blocks,use_threading=use_threading)
#
#     return {
#         'peer_height': max_height_peer,
#         'self_height': getMaxBlockHeight()
#         }


if __name__ == '__main__':
    
    x = start_node()
    #x = askPeerForBlocks('76.179.199.85', 0, 50)
    
    #x = pingPeers()
    
    #x = checkPeerBlocks(use_threading=False)
    