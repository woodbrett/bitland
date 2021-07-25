'''
Created on Jul 20, 2021

@author: brett_wood
'''
import threading 
import time
from node.information.blocks import getMaxBlockHeight, getBlockInformation,\
    getBlock
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
        print('thread: ' + str(threading.get_ident()) + '; sleep: ' + str(sleep_time))
        if sleep_time > 100:
            return False    
    
    return threading.get_ident()
    

#QUEUED PROCESS
def validateAddBlock(block_bytes, block_height=0, use_threading=True):
    
    if use_threading == True:
        thread_id = waitInBlockQueue()
    
    else:
        thread_id = True
    
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
    
    if use_threading == True:
        block_queue.remove(threading.get_ident())
    
    return add_block


#QUEUED PROCESS
def processPeerBlocks(new_blocks_hex, use_threading=True):
    
    blocks_added = 0
    blocks_removed = 0
    
    if use_threading==True:
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
        prior_block = getBlock(comparison_block_height - 1)
        
        valid_blocks = validateBlocksMemory(peer_blocks_split,prev_block,prior_block)
        
        if valid_blocks == True:
            remove = removeBlocks(comparison_block_height,self_height)
            blocks_removed = len(peer_blocks_split)
            
            if remove == True:
                validateAddBlocksAlreadyQueue(peer_blocks_split)
                blocks_added = len(peer_blocks_split)
    
    if use_threading==True:
        block_queue.remove(threading.get_ident())
                
    return blocks_added, blocks_removed


def validateBlocksMemory(blocks,start_prev_block,start_prior_block):
    
    prev_block = unhexlify(start_prev_block)
    prior_block = start_prior_block
    prior_block_bytes = unhexlify(prior_block)
    
    for i in range(0,len(blocks)):
        print('analyzing block ' + str(i))
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlockHeader(block_bytes, realtime_validation=False, prior_block=prior_block_bytes)[0]
        
        if valid_block == False:
            print('invalid block, stopping analysis')
            break
        
        prev_block = calculateHeaderHashFromBlock(blocks[i])
        prior_block_bytes = block_bytes
        
    return valid_block


def validateAddBlocksAlreadyQueue(blocks):
    
    for i in range(0,len(blocks)):
        print('analyzing block ' + str(i))
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlock(block_bytes, realtime_validation=False)
        print(valid_block)
        
        if valid_block == True:
            add_block = addBlock(block_bytes)
            print('added block ' + str(add_block))
        
        else:
            valid_block == False
        
    return valid_block
    
    
if __name__ == '__main__':

    block = '00010000000a5e161d29d884e5b147d137478c6171e62b24cdee1c723c04da33186e2dc694ed1e25f991b4c9910011c766ec29b37ba54459104290eee06dfc0c1c3c0060fe12351d0ffff0000a91a7333133353465373735353662373435613734333436623537346434633731346233353531346337323738343134643531363137303739363534363738343136393336363800e930ad00020102677d5fc4a0b96d8978fbc50b60ea1b36f53906e26bd83384a2bcd38354f41e4e0240decdae58adf8fce02f2cf2f8073db49ee2a7b2ef056f5013f1e33cf047ef30fb47a7d2ce76547f70129ac12dc606bb67ffc1cb6a1d6bf58665a42a9030d064900101010070504f4c59474f4e28282d38392e3239363837352037362e3437383534392c2d38392e3239363837352037362e35343834322c2d38392e31343932342037362e35343834322c2d38392e3135363232372037362e3437383534392c2d38392e3239363837352037362e343738353439292940d0394277127fede9f032d2f4b2454c875b341b6fb87fff81f6e4f45ed7a50c4d5e635c221a2713bcea9a8bde513ccfebbfdab55e8ce74d182365e82c5991d9a20000000000000000000000000000000000000100010001006e504f4c59474f4e28282d39332e3136343036332034342e39353132322c2d39332e3136343036332034342e38323136322c2d39332e3531353632352034342e38323136322c2d39332e3531353632352034342e39353132322c2d39332e3136343036332034342e3935313232292940bdeae1b2543ea34b59340b9ce306b9ca9f6423f2bf96fbb6a8f2936d79fd8cd314754774ab2e38f94516d6b4364dd3aeef874924294c5bc4970496b8ebccbcd90000000000000000000000000000000000'
    block_bytes = unhexlify(block)
    
    x = validateAddBlock(block_bytes, use_threading=False)
