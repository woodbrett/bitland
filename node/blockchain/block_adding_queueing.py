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
        print('thread: ' + str(threading.get_ident()) + '; sleep: ' + str(sleep_time))
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

    block = '00010000000128596e3a8c3366595d16c38d5e1c6e4480810a2fb6e8929558679eb60368ea8a6b582ff2015c4afc259feb0d391f1a7aaa51e990a44d3318b96189a50060fc4e111d0ffff0000a90de33313335346537373535366237343561373433343662353734643463373134623335353134633732373834313464353136313730373936353436373834313639333636381162e96b000203015133603c845ab7d0268c85bec310e002aefdedf9bd83fb189dc79c2fc3abbfaf004066264218daad0dac040412be6dda4d862c58a8a3d3491acfe0c77bf58b12859d1b0699a5a79d8d921a9f0eb21540d921f742dbcda02f5238a41d69bd033901fc015814c128aff69a595762d1ce28ded5f86e0ae840951bcc61e493bd6aa6878d2e004076251c18337b5ad0649bdcb02aac257e6cd57a7abc9762629b7c049874fe71539fdcc4c15771b6a0b59c66e81ccfad6967622fcfbfc3e5eb72634db7fc041c70019f6870bf482a445cf102596a55efd1ff1a35edec9dcd425cf0f3cf4478aa2e2500406f208cf7d15ed71e052b14e9bf23187ce69b3d122a278a8a1b1e9066c26dd0abd5c7cdddfaff67f6e57a2b0721a19844e3793a35fb33a223e2eeb61e008a76e00301010141504f4c59474f4e28282d38382e35393337352037362e33353336362c2d38382e35393337352037362e32363235353137363537393836392c2d38382e3731343032373430353635382037362e3236373036323136383531312c2d38382e37313037333137313238393233332037362e313631362c2d38392e3239363837352037362e313631362c2d38392e3239363837352037362e33353336362c2d38392e3239363837352037362e3437383534383938343931372c2d38392e31353632323731313236392037362e3437383534383938343931372c2d38392e31343932343030313131383133352037362e35343834322c2d38382e35393337352037362e35343834322c2d38372e3839303632352037362e35343834322c2d38372e3839303632352037362e33353336362c2d38382e35393337352037362e33353336362929408df9560d48f67fe122679245430635553b37f6860a3b261ef504a4df19286f90c46a6452606a56fa569db1edd85a282df3513afce43aaef9eb87f97bb457789c01010090504f4c59474f4e28282d38382e35393337352037362e32363235353137363537393836392c2d38382e35393337352037362e313631362c2d38382e37313037333137313238393233332037362e313631362c2d38382e3731343032373430353635382037362e3236373036323136383531312c2d38382e35393337352037362e32363235353137363537393836392929400cffde9bb11a7778d10b32582a208a4674fef749bbcc815c9fa9297b4d54025134dd56ba003697ff57f0493debd003e45431d275aabb9fdf2f8f4a3fb46c358402010090504f4c59474f4e28282d38392e3239363837352037362e3437383534383938343931372c2d38392e3239363837352037362e35343834322c2d38392e31343932343030313131383133352037362e35343834322c2d38392e31353632323731313236392037362e3437383534383938343931372c2d38392e3239363837352037362e343738353438393834393137292940f10bdaab7272758c8d8507e337bf8f4f917716c5852dc61419832a39c2ec96a6a770142d44ff2cba814caf201f781b0c9232d4ed918b1d07a0ef5e837fc55f7b00000000c350006400000000c3500064443331343735383332333837393463366135363537373537383337373737333334353535313339343634323334346436653463343833343535346235343530346233323761000100010001006c504f4c59474f4e28282d39362e3637393638382034392e35343837382c2d39362e3637393638382034392e34303736362c2d39372e30333132352034392e34303736362c2d39372e30333132352034392e35343837382c2d39362e3637393638382034392e353438373829294084beff2a5219da491b7d45e84d5d7b952f3e119c4bddf391a0bdb4057b5b4ab9130268149567fa3fd2efd156c58af230480c9f95fd6c70334c98055800453e9f0000000000000000000000000000000000'
    block_bytes = unhexlify(block)
    
    x = validateAddBlock(block_bytes)
