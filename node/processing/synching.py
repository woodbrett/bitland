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
    attemptToConnectToNewPeer, deletePeer, peerCount, resetPeers, queryPeers
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
from system_variables import peering_port, min_peer_count, node_network
from utilities.time_utils import getTimeNowSeconds
from utilities.bitcoin.bitcoin_requests import getBestBlockHash
from utilities import bitcoin
from utilities.connectivity import checkInternetConnection

global bitcoin_connection 
global peer_count 
global bitland_synched
global bitcoin_synched
global internet_connection

bitcoin_connection = False
peer_count = 0
bitland_synched = False
bitcoin_synched = True
internet_connection = False

def start_node():

    print('checking internet connection')
    internet_connection = checkInternetConnection()

    print('resetting peers')
    resetPeers()
    
    print('pinging peers')
    pingPeers()
    
    print('sleeping 10 seconds to sort out peering')
    time.sleep(10)
    
    return True


def run_node(initial_synch=False):
    
    global bitcoin_connection 
    global peer_count 
    global bitland_synched
    global bitcoin_synched
    global internet_connection
    
    #pingPeers(peer_types=['connected','unpeered'])
    
    if initial_synch == True:   
        initialSynch()
    
    while True:

        if internet_connection == False:
            if checkInternetConnection() == True:
                internet_connection = True
                resetPeers()
        
        if internet_connection == True:
            peers = pingPeers(peer_types=['connected','unpeered'])
            peer_count = peers.get('peer_count')
        
            if peer_count == 0:
                internet_connection = checkInternetConnection()
        
        best_bitcoin_block_hash = getBestBlockHash()
        if best_bitcoin_block_hash == None:
            bitcoin_connection = False
            bitcoin_synched = False
            bitland_synched = False
        else:
            bitcoin_connection = True

        node_status = getNodeStatus()
        
        if node_status.get('node_connectivity') == True:
                            
            print('synching bitcoin')
            synch_bitcoin = synchBitcoin()
            bitcoin_connection = synch_bitcoin
            bitcoin_synched = synch_bitcoin
            
            print('bitcoin connection status: ' + str(bitcoin_connection))
          
            print('checking peer blocks')
            bitland_synch = checkPeerBlocks(use_queue=True)
            bitland_synched = bitland_synch.get('synched')
            #t3 = threading.Thread(target=checkPeerBlocks,args=(True,),daemon=True)
            #t3.start()
    
        print('node status:')
        print(getNodeStatus())
        
        time.sleep(60)


def pingPeers(peer_types=['connected','unpeered','offline',None]):

    ping = messageAllKnownPeers('/peer/peering/ping', rest_type='get',peer_types=peer_types,message_type='ping peers')
    
    for i in range(0,len(ping)):
        
        peer_ip_address= ping[i].get('peer_ip_address')
        peer_port= ping[i].get('peer_port')
        peer_response = ping[i].get('response')
        
        if peer_response == 'error calling peer':
            updatePeer(ip_address=peer_ip_address,port=peer_port,status='offline')
        
        elif peer_response.get('message') == 'Not authenticated as peer':
            attemptToConnectToNewPeer(bitland_version, peering_port, getTimeNowSeconds(), node_network, peer_ip_address, peer_port)
        
        else:
            updatePeer(ip_address=peer_ip_address,port=peer_port,status='connected')
    
    count = peerCount()
    
    return {
        "peer_count": count
    }


def initialSynch():
    
    print('performing initial synch')
    
    peer_count = peerCount()
    while peer_count == 0:
        print('peer count 0, waiting')
        time.sleep(10)
        peer_count = peerCount()
    
    synched = False
    while synched == False:
        synch_peer = checkPeerBlocks(use_queue=False)
        synched = synch_peer.get('peer_height') == synch_peer.get('self_height')
    

def getNodeStatus():
    
    node_connectivity = (bitcoin_connection and peer_count >= min_peer_count and internet_connection)
    node_synched = (bitcoin_synched and bitland_synched)
    bitland_height = getMaxBlockHeight()
    
    return {
        "bitcoin_connection": bitcoin_connection,
        "peer_count": peer_count,
        "bitland_synched": bitland_synched,
        "bitcoin_synched": bitcoin_synched,
        "node_connectivity": node_connectivity,
        "bitland_height": bitland_height,
        "node_synched": node_synched,
        "internet_connection": internet_connection
        }


if __name__ == '__main__':
    
    x = start_node()
    #x = askPeerForBlocks('76.179.199.85', 0, 50)
    
    #x = pingPeers()
    
    