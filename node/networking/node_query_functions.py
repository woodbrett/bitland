'''
Created on Jul 12, 2021

@author: brett_wood
'''
#this is for storing the functions to support the peer blockchain APIs

from node.information.blocks import (
    getMaxBlockInformation,
    getBlock,
    getBlocks
    )


def get_block_height_peer(): 
    
    return getMaxBlockInformation()


def get_block_by_height(block_height):
    
    block = getBlock(block_height)
    
    return block


def get_blocks_start_end(start_block, end_block):
    
    blocks = getBlocks(start_block, end_block)
    
    return blocks







if __name__ == '__main__':
    
    print(get_block_height_peer().id)