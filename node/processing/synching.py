'''
Created on Jul 14, 2021

@author: brett_wood
'''
from node.information.blocks import getBlocks
from node.blockchain.block_serialization import deserialize_block
from binascii import unhexlify,hexlify
from node.networking.node_query_functions import get_blocks_start_end
import json

def ask_peers_for_height():
    
    return True


def process_blocks(blocks):
    
    return True


if __name__ == '__main__':
    
    blocks = get_blocks_start_end(1,10)
    print(blocks)
    
    blocks_bytes = unhexlify(blocks)
    
    print(deserialize_block(blocks_bytes))



    
    
    
