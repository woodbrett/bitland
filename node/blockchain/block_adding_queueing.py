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

    #0001000000089452054c898184d204a09d5d1fbb49729edd9b12ecaa0c4cb72856081f533960e6e0b67d26ca30a9ae0cb38193c07ae2bb4ef8403e8e1d4221907e870060fe63991d0ffff0000a91d1363236333331373133323736366336313330333236623736373337333663373936363634363733333734373036343737373433363737363836643636373237333634366236333337363433303662366237373733022be5fd00020301c92ffed21a11db4e5829ce5f027ff09a669aadc78129a6e18432308cdca77ec70040447c07fd5e506d3a66e59327330141670cfd304485b97ef9eea8e4942ab7b0c2b095006aa8615d51763008b20d165c8bd896d145e2b39c1d066e456905d5f9b40136b5f5868ebb7895f4110a3b8a0438d755a0e2c729986ef9ce9f16723f4bed810040607bc62b87148922f1576a948ccf6f2c899e30f702a5a846af170cb5b7ec1a27573a2ccfc3fdae1f4a311e2b6fb3e0eba470d5476e1a364f8efa54a542e8a87d015cc1181c5528c88f4d4a8e5e9c56d43801e7f363d9c2a3140d9dbd59d4ce0d3d0040ab2696f2ec1100b1d8acfd2455f741c03a8e4d9cf932ffacbe6670f17ca9b279cde018471de24565a6c2609c3fa7e3360d0bc691b7b8fd116d146249019ab01403010100d14d554c5449504f4c59474f4e2828282d39342e32313837352034362e363633322c2d39342e32313837352034362e35323936342c2d39342e3430393133352034362e35323936342c2d39342e3333333138392034362e363633322c2d39342e32313837352034362e3636333229292c28282d39342e32313837352034362e323633362c2d39342e32313837352034362e31333039342c2d39342e3437343132372034362e31333039342c2d39342e3432323533372034362e323633362c2d39342e32313837352034362e3236333629292940a5f04796f6171761240579c7757e94932b6456174b3a12775f3a969cd4d826f1d6b5891433c44cd0fa7a7163a4756eb7ae9030b2ec0981dec00166cd695eaa5c010100db4d554c5449504f4c59474f4e2828282d39342e3437343132372034362e31333039342c2d39342e3537303331332034362e31333039342c2d39342e3537303331332034362e323633362c2d39342e3432323533372034362e323633362c2d39342e3437343132372034362e313330393429292c28282d39342e3932313837352034372e33333630342c2d39342e3932313837352034372e32303038362c2d39352e3237333433382034372e32303038362c2d39352e3237333433382034372e33333630342c2d39342e3932313837352034372e3333363034292929403297126344dbc061ed3157e7ecace14bbda9015e26ad1a4a09db287538c1ddcfb2657343971e9c32f539c6b541be4810c2af3640e24e212b8844e9a394bb49040201006c504f4c59474f4e28282d39342e3430393133352034362e35323936342c2d39342e3537303331332034362e35323936342c2d39342e3537303331332034362e363633322c2d39342e3333333138392034362e363633322c2d39342e3430393133352034362e3532393634292940c39039aa3affdf4ec2b9636e2ca0fd6607b72026d662980727f1c41d841b754de3269343de805c20392f90da6c6803e724f91fb91b4715f33e4cbb2ed4c64e3600000000c35007d000000000c35007d0543632363333313731333237363663363133303332366237363733373336633739363636343637333337343730363437373734333637373638366436363732373336343662363333373634333036623662373737330001000100010073504f4c59474f4e28282d3130302e3139353331332035312e38363535362c2d3130302e3139353331332035312e37313734322c2d3130302e3534363837352035312e37313734322c2d3130302e3534363837352035312e38363535362c2d3130302e3139353331332035312e38363535362929403fcb003ba27ef184bcf3f20e7c38c651695f309f8afcd87918d10533db0269230a911bfc401f4eaf8ba13bf8bf7f0628527d7c972702578294aaaf394ad03f5b0000000000000000000000000000000000
    block = '0001000000089452054c898184d204a09d5d1fbb49729edd9b12ecaa0c4cb72856081f533960e6e0b67d26ca30a9ae0cb38193c07ae2bb4ef8403e8e1d4221907e870060fe63991d0ffff0000a91d1363236333331373133323736366336313330333236623736373337333663373936363634363733333734373036343737373433363737363836643636373237333634366236333337363433303662366237373733022be5fd00020301c92ffed21a11db4e5829ce5f027ff09a669aadc78129a6e18432308cdca77ec70040447c07fd5e506d3a66e59327330141670cfd304485b97ef9eea8e4942ab7b0c2b095006aa8615d51763008b20d165c8bd896d145e2b39c1d066e456905d5f9b40136b5f5868ebb7895f4110a3b8a0438d755a0e2c729986ef9ce9f16723f4bed810040607bc62b87148922f1576a948ccf6f2c899e30f702a5a846af170cb5b7ec1a27573a2ccfc3fdae1f4a311e2b6fb3e0eba470d5476e1a364f8efa54a542e8a87d015cc1181c5528c88f4d4a8e5e9c56d43801e7f363d9c2a3140d9dbd59d4ce0d3d0040ab2696f2ec1100b1d8acfd2455f741c03a8e4d9cf932ffacbe6670f17ca9b279cde018471de24565a6c2609c3fa7e3360d0bc691b7b8fd116d146249019ab01403010100d14d554c5449504f4c59474f4e2828282d39342e32313837352034362e363633322c2d39342e32313837352034362e35323936342c2d39342e3430393133352034362e35323936342c2d39342e3333333138392034362e363633322c2d39342e32313837352034362e3636333229292c28282d39342e32313837352034362e323633362c2d39342e32313837352034362e31333039342c2d39342e3437343132372034362e31333039342c2d39342e3432323533372034362e323633362c2d39342e32313837352034362e3236333629292940a5f04796f6171761240579c7757e94932b6456174b3a12775f3a969cd4d826f1d6b5891433c44cd0fa7a7163a4756eb7ae9030b2ec0981dec00166cd695eaa5c010100db4d554c5449504f4c59474f4e2828282d39342e3437343132372034362e31333039342c2d39342e3537303331332034362e31333039342c2d39342e3537303331332034362e323633362c2d39342e3432323533372034362e323633362c2d39342e3437343132372034362e313330393429292c28282d39342e3932313837352034372e33333630342c2d39342e3932313837352034372e32303038362c2d39352e3237333433382034372e32303038362c2d39352e3237333433382034372e33333630342c2d39342e3932313837352034372e3333363034292929403297126344dbc061ed3157e7ecace14bbda9015e26ad1a4a09db287538c1ddcfb2657343971e9c32f539c6b541be4810c2af3640e24e212b8844e9a394bb49040201006c504f4c59474f4e28282d39342e3430393133352034362e35323936342c2d39342e3537303331332034362e35323936342c2d39342e3537303331332034362e363633322c2d39342e3333333138392034362e363633322c2d39342e3430393133352034362e3532393634292940c39039aa3affdf4ec2b9636e2ca0fd6607b72026d662980727f1c41d841b754de3269343de805c20392f90da6c6803e724f91fb91b4715f33e4cbb2ed4c64e3600000000c35007d000000000c35007d0543632363333313731333237363663363133303332366237363733373336633739363636343637333337343730363437373734333637373638366436363732373336343662363333373634333036623662373737330001000100010073504f4c59474f4e28282d3130302e3139353331332035312e38363535362c2d3130302e3139353331332035312e37313734322c2d3130302e3534363837352035312e37313734322c2d3130302e3534363837352035312e38363535362c2d3130302e3139353331332035312e38363535362929403fcb003ba27ef184bcf3f20e7c38c651695f309f8afcd87918d10533db0269230a911bfc401f4eaf8ba13bf8bf7f0628527d7c972702578294aaaf394ad03f5b0000000000000000000000000000000000'
    block_bytes = unhexlify(block)
    
    x = validateAddBlock(block_bytes, use_threading=False)
