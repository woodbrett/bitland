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
from utilities.hashing import calculateHeaderHashFromBlock

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
        new_blocks = ask_peer_for_blocks(max_height_peer, max(self_height - 5,1), min(max_height-self_height,50)+self_height)
        
        peer_blocks = json.loads(new_blocks.get('blocks'))
        start_block_height = int(new_blocks.get('start_block_height'))
        peer_next_block = peer_blocks[self_height - start_block_height + 1]
        
        next_block_header = deserialize_block(unhexlify(peer_next_block))[0]
        next_block_prev_block = next_block_header[1]
        
        self_height_hash = unhexlify(getBlockInformation(block_id=self_height).header_hash)
              
        if next_block_prev_block == self_height_hash:
            process_blocks(peer_blocks[peer_next_block:])
        
        #UPDATE else logic in case the peer has a longer divergent chain
        #haven't tested this yet
        elif unhexlify(getBlockInformation(block_id=start_block_height).header_hash) == calculateHeaderHashFromBlock(unhexlify(peer_blocks[0])):
            
            comparison_block_height = start_block_height
            
            #move to function compare_chains_find_split 
            for i in range(0,(self_height - start_block_height)):
                if getBlockInformation(block_id=i+start_block_height).header_hash != calculateHeaderHashFromBlock(unhexlify(peer_blocks[i])):
                    peer_blocks_split = peer_blocks[i:]
                    break
                comparison_block_height = comparison_block_height + 1
            
            prev_block = getBlockInformation(comparison_block_height).prev_block
            valid_blocks = process_blocks_memory(peer_blocks_split)
            
            if valid_blocks == True:
                1
                
    return None


def process_blocks_memory(blocks,start_prev_block):
    
    prev_block = start_prev_block
    
    for i in range(0,len(blocks)):
        print('analyzing block ' + str(i))
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlock(blocks[i], realtime_validation=False, prev_block_input=prev_block)
        
        if valid_block == False:
            print('invalid block, stopping analysis')
            break
        
        prev_block = deserialize_block(unhexlify(blocks[i]))[0][1]
        
    return valid_block


def process_blocks(blocks):
    
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
        
    return None
    

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
    
    #x = synch_node()
    
    low = 6
    high = 9
    
    for i in range(0, high+1-low):
        print(high-i)
    
    
    
