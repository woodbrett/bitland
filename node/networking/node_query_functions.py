'''
Created on Jul 12, 2021

@author: brett_wood
'''
#this is for storing the functions to support the peer blockchain APIs
import json

from node.information.blocks import (
    getMaxBlockInformation,
    getBlock,
    getBlocksSerialized
    )


def getBlockHeightPeer(): 
    
    return getMaxBlockInformation()


def getBlockByHeight(block_height):
    
    block = getBlock(block_height)
    
    return block


def getBlocksStartEnd(start_block, end_block):
    
    blocks = getBlocksSerialized(start_block, end_block)
    start_block = blocks[0][0]
    block_list = []
    for i in range(0,len(blocks)):
        block_list.append(blocks[i][1])
    
    return start_block, block_list







if __name__ == '__main__':
    
    print(getBlocksStartEnd(1, 5))
    
    print(getBlockHeightPeer().id)