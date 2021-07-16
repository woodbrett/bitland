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
from node.blockchain.validate_block import validateBlock
from node.blockchain.block_operations import addBlock

def synch_node():
    
    peer_heights = ask_peers_for_height()
    self_height = getMaxBlockHeight()
    max_height = self_height
    max_height_peer = 'self'
    
    for i in range(0,len(peer_heights)):
        if peer_heights[i][1].get('block_height') > max_height:
            max_height= peer_heights[i][1].get('block_height')
            max_height_peer = peer_heights[i][0]
    
    if max_height_peer != 'self':
        #UPDATE to only ask for max of X blocks, 50?
        new_blocks = ask_peer_for_blocks(max_height_peer, max(self_height - 3,1), min(max_height-self_height,50)+self_height)
        
        peer_blocks = json.loads(new_blocks.get('blocks'))
        start_block_height = int(new_blocks.get('start_block_height'))
        next_block_list_start = self_height - start_block_height + 1
        next_block = peer_blocks[next_block_list_start]
        
        next_block_header = deserialize_block(unhexlify(next_block))[0]
        next_block_prior_block_header = next_block_header[1]
        
        self_header = unhexlify(getBlockInformation(block_id=self_height).header_hash)
              
        if next_block_prior_block_header == self_header:
            process_blocks(peer_blocks[next_block_list_start:])
        
        #UPDATE else logic in case the peer has a longer divergent chain
                
    return True


def process_blocks(blocks=[]):
    
    for i in range(0,len(blocks)):
        print('analyzing block ' + str(i))
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlock(block_bytes, False)
        print(valid_block)
        
        if valid_block == True:
            add_block = addBlock(block_bytes)
            print('added block ' + str(add_block))
        
        else:
            print('invalid block, stopping additions')
            break
        
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
    
    x = synch_node()


    
    
    
