'''
Created on Jul 20, 2021

@author: brett_wood
'''
import threading 
import time
from node.information.blocks import (
    getMaxBlockHeight, 
    getBlock, getBlockSerialized
    )
from node.blockchain.validate_block import validateBlock, validateBlockHeader
from node.blockchain.block_operations import addBlock, removeBlocks
from utilities.hashing import calculateHeaderHashFromBlock
import json
from node.blockchain.block_serialization import deserialize_block
from binascii import (unhexlify,hexlify)
from node.blockchain.header_serialization import deserialize_block_header,\
    serialize_block_header
from utilities.bitcoin.bitcoin_transactions import synchWithBitcoin

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
def validateAddBlock(block_bytes, block_height=0, use_threading=True, realtime_validation=True):
    
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
            if validateBlock(block_bytes, realtime_validation=realtime_validation) == True:
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
    
    self_height_hash = unhexlify(getBlock(block_id=self_height).get('header_hash'))
            
    self_base_hash = unhexlify(getBlock(block_id=start_block_height).get('header_hash'))
    peer_base_hash = calculateHeaderHashFromBlock(peer_blocks[0])
        
    if next_block_prev_block == self_height_hash:
        validateAddBlocksAlreadyQueue(peer_blocks[peer_next_block_index:])
        blocks_added = len(peer_blocks[peer_next_block_index:])
    
    #UPDATE else logic in case the peer has a longer divergent chain
    #haven't tested this yet
    
    elif self_base_hash == peer_base_hash: 
        
        comparison_block_height = start_block_height
        
        #move to function compare_chains_find_split 
        for i in range(0,(self_height - start_block_height + 1)):
            
            self_hash_i = unhexlify(getBlock(block_id=i+start_block_height).get('header_hash'))
            peer_hash_i = calculateHeaderHashFromBlock(peer_blocks[i])
            
            if self_hash_i != peer_hash_i:
                peer_blocks_split = peer_blocks[i:]
                break
            
            comparison_block_height = comparison_block_height + 1
        
        prev_block = getBlock(comparison_block_height).get('prev_block')
        prior_block = getBlockSerialized(comparison_block_height - 1)
        
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
        print('analyzing block ' + str(i), flush=True)
        block_bytes = unhexlify(blocks[i])
        valid_block = validateBlock(block_bytes, realtime_validation=False)
        print(valid_block)
        
        if valid_block == True:
            add_block = addBlock(block_bytes)
            print('added block ' + str(add_block), flush=True)
        
        else:
            valid_block == False
        
    return valid_block


def synchBitcoin(use_threading=True):
    
    if use_threading == True:
        thread_id = waitInBlockQueue()
    
    synchWithBitcoin()
    
    if use_threading == True:
        block_queue.remove(threading.get_ident())  
        
    return True  
    
    
if __name__ == '__main__':

    block = '00010000000d75478bbae073ef2f49eab29458637335c1b32fb54ab739e3949c5fbce59307f8c93b81b8c1c50a5b037b0e80d573902dd02355f458c898f49d60a491006115afcf1d0ffff0000a9ca3002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b777300000000000000b94a31000100010001005a504f4c59474f4e28282d34322e313837352038372e30313532342c2d34322e313837352038362e38303337342c2d34352038362e38303337342c2d34352038372e30313532342c2d34322e313837352038372e3031353234292940e812471dcc52aa292aae655d6667460b2c8393cc2ef940878889adcf76f8b67d8e54998d2bb4110a1e86a70b315507e4766f60a0853a50be249e24d60855e00c0000000000000000000000000000000000'
    block_bytes = unhexlify(block)
    
    #print(deserialize_block(block_bytes))
    #desrialized_header = deserialize_block_header(block_bytes)
    #print(hexlify(serialize_block_header(desrialized_header[0],desrialized_header[1],desrialized_header[2],desrialized_header[3],desrialized_header[4],desrialized_header[5],desrialized_header[6],desrialized_header[7])))
    #prior_block_hash = calculateHeaderHashFromBlock(block_bytes=prior_block)
    #prior_block_bitcoin_height = prior_block_header[5]    
    
    x = validateAddBlock(block_bytes, use_threading=False,realtime_validation=False)
