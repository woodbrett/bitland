'''
Created on Jul 20, 2021

@author: brett_wood
'''
import threading 
import time
from node.information.blocks import getMaxBlockHeight, getBlockInformation
from node.blockchain.validate_block import validateBlock, validateBlockHeader
from node.blockchain.block_operations import addBlock, removeBlocks
from utilities.hashing import calculateHeaderHashFromBlock
import json
from node.blockchain.block_serialization import deserialize_block
from binascii import unhexlify

block_queue = []

def waitInBlockQueue():
#all processes validating and adding blocks should come through this to avoid conflicting adds

    block_queue.append(threading.get_ident())
    print(block_queue)
    
    print(threading.get_ident())
    time.sleep(5)
    sleep_time = 0

    while block_queue[0] != threading.get_ident():
        time.sleep(1)   
        sleep_time = sleep_time + 1
        print('thread: ' + str(threading.get_ident() + '; sleep: ' + str(sleep_time)))
        if sleep_time > 100:
            return False    
    
    return threading.get_ident()
    

#QUEUED PROCESS
def validateAddBlock(block_bytes, block_height=0):
    
    thread_id = waitInBlockQueue()
    
    add_block = True
        
    if thread_id == False:
        add_block = False
    
    if add_block == True:
        self_height = getMaxBlockHeight()
    
        if block_height != 0 and block_height > self_height + 1:
            add_block = False
        
        elif block_height == 0 or block_height == self_height + 1:
            if validateBlock(block_bytes) == True:
                new_block = addBlock(block_bytes)
                add_block = True
            else:
                add_block = False
                
        #UPDATE make sure it didn't not validate because of something wrong, but rather different chain (prior block different)
        #right now it just sends it to synch node to handle, but this should be integrated more directly
        else:
            add_block = False
    
    block_queue.remove(threading.get_ident())
    
    return add_block


#QUEUED PROCESS
def processPeerBlocks(new_blocks_hex):
    
    blocks_added = 0
    blocks_removed = 0
    
    thread_id = waitInBlockQueue()
    self_height = getMaxBlockHeight()
    
    peer_blocks = json.loads(new_blocks_hex.get('blocks'))
    start_block_height = int(new_blocks_hex.get('start_block_height'))
    peer_next_block_index = self_height - start_block_height + 1
    peer_next_block = peer_blocks[peer_next_block_index]
    
    next_block_header = deserialize_block(unhexlify(peer_next_block))[0]
    next_block_prev_block = next_block_header[1]
    
    self_height_hash = unhexlify(getBlockInformation(block_id=self_height).header_hash)
            
    self_base_hash = unhexlify(getBlockInformation(block_id=start_block_height).header_hash)
    peer_base_hash = calculateHeaderHashFromBlock(peer_blocks[0])
    
    if next_block_prev_block == self_height_hash:
        validateAddBlocksAlreadyQueue(peer_blocks[peer_next_block_index:])
        blocks_added = len(peer_blocks[peer_next_block_index:])
    
    #UPDATE else logic in case the peer has a longer divergent chain
    #haven't tested this yet
    
    elif self_base_hash == peer_base_hash: #unhexlify(getBlockInformation(block_id=start_block_height).header_hash) == calculateHeaderHashFromBlock(unhexlify(peer_blocks[0])):
        
        comparison_block_height = start_block_height
        
        #move to function compare_chains_find_split 
        for i in range(0,(self_height - start_block_height + 1)):
            
            self_hash_i = unhexlify(getBlockInformation(block_id=i+start_block_height).header_hash)
            peer_hash_i = calculateHeaderHashFromBlock(peer_blocks[i])
            
            if self_hash_i != peer_hash_i:
                peer_blocks_split = peer_blocks[i:]
                break
            comparison_block_height = comparison_block_height + 1
        
        prev_block = getBlockInformation(comparison_block_height).prev_block
        
        valid_blocks = validateBlocksMemory(peer_blocks_split,prev_block)
        
        if valid_blocks == True:
            remove = removeBlocks(comparison_block_height,self_height)
            blocks_removed = len(peer_blocks_split)
            
            if remove == True:
                validateAddBlocksAlreadyQueue(peer_blocks_split)
                blocks_added = len(peer_blocks_split)

    block_queue.remove(threading.get_ident())
                
    return blocks_added, blocks_removed


def validateBlocksMemory(blocks,start_prev_block):
    
    prev_block = unhexlify(start_prev_block)
    
    for i in range(0,len(blocks)):
        print('analyzing block ' + str(i))
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlockHeader(block_bytes, realtime_validation=False, prev_block_input=prev_block)[0]
        
        if valid_block == False:
            print('invalid block, stopping analysis')
            break
        
        prev_block = calculateHeaderHashFromBlock(blocks[i])
        
    return valid_block


def validateAddBlocksAlreadyQueue(blocks):
    
    for i in range(0,len(blocks)):
        print('analyzing block ' + str(i))
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlock(block_bytes, False)
        print(valid_block)
        
        if valid_block == True:
            add_block = addBlock(block_bytes)
            print('added block ' + str(add_block))
        
        else:
            valid_block == False
        
    return valid_block
    
    
if __name__ == '__main__':

    block = '000100000001c64a231647a2498657c8ec9eb474d263e70410734cbe3d979948760198c65f375388348d3c2d64b82a90019703ee572b00bf40e406d662f5ab84fce90060f77db31d0ffff0000a8ec9333133353465373735353662373435613734333436623537346434633731346233353531346337323738343134643531363137303739363534363738343136393336363802af92370001000100010067504f4c59474f4e28282d38302e31353632352037392e39303237322c2d38302e31353632352037392e37373334382c2d38312e353632352037392e37373334382c2d38312e353632352037392e39303237322c2d38302e31353632352037392e3930323732292940ef785f1d1375cba2f8bce50f2fb546a9dd0fda1c3019bcbfd4126b3255103d6beaa6a23ec56d898cd9412120fcc1b0c94765b625303128d8f86688de77671ed00000000000000000000000000000000000'
    block_bytes = unhexlify(block)
    
    x = validateAddBlock(block_bytes)
