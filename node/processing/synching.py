'''
Created on Jul 14, 2021

@author: brett_wood
'''
from node.information.blocks import getBlocks
from node.blockchain.block_serialization import deserialize_block
from binascii import unhexlify,hexlify
from node.networking.node_query_functions import get_blocks_start_end
import json
from node.networking.peering_functions import message_all_connected_peers

#UPDATE
def ask_peers_for_height():
    
    heights = message_all_connected_peers('/peer/node_queries/getBlockHeight', rest_type='get')
    
    return heights


#UPDATE
def ask_peer_for_blocks(start_block, end_blocks):
    
    return True


#UPDATE
def process_blocks(blocks):
    
    return True


if __name__ == '__main__':
    
    print(ask_peers_for_height())



    
    
    
