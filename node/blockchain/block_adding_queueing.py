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
from node.blockchain.block_serialization import deserializeBlock
from binascii import (unhexlify,hexlify)
from node.blockchain.header_serialization import (
    deserializeBlockHeader,
    serializeBlockHeader
    )
from utilities.bitcoin.bitcoin_transactions import synchWithBitcoin,\
    realtimeSynchWithBitcoin

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
def validateAddBlock(block_bytes, block_height=0, use_threading=True, realtime_validation=True, send_to_peers=False):
    
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
    
    next_block_header = deserializeBlock(unhexlify(peer_next_block))[0]
    next_block_prev_block = next_block_header.get('prev_block')
    
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
    
    realtimeSynchWithBitcoin()
    
    if use_threading == True:
        block_queue.remove(threading.get_ident())  
        
    return True  
    
    
if __name__ == '__main__':


    blocks = ['00010000000b139ae9f27e22fc94792111c7946070a398b42967e01b908b6a3c165de3c35f383abfe1bedfb54cab6748b18a11f09869b9507905a48d15273bcc108f0061216e111d0ffff000000000000000000006040752a1d61728dcc15e438158a267e2c9bef17de2c4000aa235b29582960bdaffa8384a57cf0ed23535873794d28118aadbae7acac8b923a2bf002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b7773000000000000088e310e0001000100010068504f4c59474f4e28282d39322e3130393337352037322e39303838322c2d39322e3130393337352037322e373534322c2d39322e383132352037322e373534322c2d39322e383132352037322e39303838322c2d39322e3130393337352037322e3930383832292940593cb16d7eb907bb304a4826cb1b60093953ba3b315f79ba1240d6d694a0e8bf411594ba69bf2abf7cd102e29ada4326587d7da322e18e23ccdd7092e39d93740000000000000000000000000000000000']

    for i in range(0, len(blocks)):
        block = blocks[i]
        #'0001000000093efc6f8a17178ee0fd9811f77d8b67a67f4a201f1efcdef814428a5da4b7b6464e99f63844fa217f87f4920f3e017d96964eef1df3419df68bbedf5700611699121d0ffff0000a9d0e002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b77730000000000001a8d93a5000100010001005e504f4c59474f4e28282d35302e3632352038362e303639372c2d35302e3632352038352e39303636322c2d35332e343337352038352e39303636322c2d35332e343337352038362e303639372c2d35302e3632352038362e3036393729294060b52eb39b4331122a96562734d86c9d798953717e40dbd3706c8b9ca557b7df6da14d284d2d6ce93140f134b747fe6ecc07701c5bb270078b70527f6354bcb30000000000000000000000000000000000'
        block_bytes = unhexlify(block)
        
        #print(deserializeBlock(block_bytes))
        #desrialized_header = deserializeBlockHeader(block_bytes)
        #print(hexlify(serializeBlockHeader(desrialized_header[0],desrialized_header[1],desrialized_header[2],desrialized_header[3],desrialized_header[4],desrialized_header[5],desrialized_header[6],desrialized_header[7])))
        #prior_block_hash = calculateHeaderHashFromBlock(block_bytes=prior_block)
        #prior_block_bitcoin_height = prior_block_header[5]    
        
        x = validateAddBlock(block_bytes, use_threading=False,realtime_validation=False)
    
    
    
    
    
    
