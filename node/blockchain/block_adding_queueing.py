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


    blocks = ['0001000000040fcef41a2b11dadabe229901e8f717f8218a9f19c61fa754cae03c185db0cecb8d5a4407a70f0c36e3600456b2fd1eb0349e503355645974d463e91c00611b42e11d0ffff00000000000000000000d412f0527dc7630e76b62c42c670a395bf7d99e89b4a4000a9f4d09af9848e4d517de3f0d734ffa17d74384ec166d66a36ad95a01eb7f8f474da5002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b77730000000000001889b9da0002010186a376a1e641a30099a01abdf6f1f18dacd74e08b32c6e95df3c46373a8c07fa01402fb61fa344ab20501001ad668db982434ac5d2b9fecab0906b23dd8c5cf821fc6b297950a6ccc0386d92001f02d59c850e51a20dab3990e316d644021808c8c001010100dd4d554c5449504f4c59474f4e2828282d35392e303632352038342e363538352c2d35392e303632352038342e34313839322c2d36302e34363837352038342e34313839322c2d36302e34363837352038342e363538352c2d35392e303632352038342e3635383529292c28282d35382e3637373238322038342e363538352c2d35392e303632352038342e363538352c2d35392e303632352038342e39303934322c2d35392e303632352038352e30333935362c2d35382e3631353438392038352e30333935362c2d35382e3637373238322038342e3635383529292940c7fd895b5a7514a436d689a0b41606671fb02e4b85a5ae25d41d1a786b3792385391b740ec96a71bffc14f0c12ffdb88d37c65f04a704f8047918c8dc2bb59d900000000000000000000000000000000000001000100010067504f4c59474f4e28282d36332e32383132352038342e31383930362c2d36332e32383132352038332e39363830322c2d36342e363837352038332e39363830322c2d36342e363837352038342e31383930362c2d36332e32383132352038342e3138393036292940834cded3576ab113c359074e17934eabb967716fd8fe91c51d0c14a92d22f607a811b143427d494df660ddc13e038e5ea5dd8d01565645a809802efcc6937cad0000000000000000000000000000000000']

    for i in range(0, len(blocks)):
        block = blocks[i]
        #'0001000000093efc6f8a17178ee0fd9811f77d8b67a67f4a201f1efcdef814428a5da4b7b6464e99f63844fa217f87f4920f3e017d96964eef1df3419df68bbedf5700611699121d0ffff0000a9d0e002a6263317132766c6130326b7673736c796664673374706477743677686d667273646b633764306b6b77730000000000001a8d93a5000100010001005e504f4c59474f4e28282d35302e3632352038362e303639372c2d35302e3632352038352e39303636322c2d35332e343337352038352e39303636322c2d35332e343337352038362e303639372c2d35302e3632352038362e3036393729294060b52eb39b4331122a96562734d86c9d798953717e40dbd3706c8b9ca557b7df6da14d284d2d6ce93140f134b747fe6ecc07701c5bb270078b70527f6354bcb30000000000000000000000000000000000'
        block_bytes = unhexlify(block)
        
        #print(deserialize_block(block_bytes))
        #desrialized_header = deserialize_block_header(block_bytes)
        #print(hexlify(serialize_block_header(desrialized_header[0],desrialized_header[1],desrialized_header[2],desrialized_header[3],desrialized_header[4],desrialized_header[5],desrialized_header[6],desrialized_header[7])))
        #prior_block_hash = calculateHeaderHashFromBlock(block_bytes=prior_block)
        #prior_block_bitcoin_height = prior_block_header[5]    
        
        x = validateAddBlock(block_bytes, use_threading=False,realtime_validation=False)
    
    
    
    
    
    
