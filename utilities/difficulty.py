'''
Created on Nov 18, 2020

@author: brett_wood
'''

from codecs import decode, encode
from binascii import hexlify, unhexlify
from node.blockchain.global_variables import (
    target_timespan_bitcoin_blocks,
    starting_bits,
    difficulty_adjustment_blocks
    )
from node.information.blocks import (
    getPriorBlock,
    getMaxBlock,
    getBlock
    )

def getBitsFromTarget(target):
    bitlength = target.bit_length() + 1 #look on bitcoin cpp for info
    size = (bitlength + 7) / 8
    size = int(size)
    value = target >> 8 * (size - 3)
    value |= size << 24 #shift size 24 bits to the left, and taks those on the front of compact
    
    value = hex(value)
    
    return value


def getTargetFromBits(bits):
    
    bits_int = int.from_bytes(bits, byteorder='big')
    
    exp = bits_int >> 24
    mant = bits_int & 0xffffff
    target_hexstr = '%064x' % (mant * (1<<(8*(exp - 3))))
    target_bytes = decode(target_hexstr, "hex")
    
    return target_bytes


def getBitsCurrentBlock():
    
    previous_block = getMaxBlock()
    
    if previous_block == 0:
        bits = starting_bits #0x1d00ffff
        return bits
        #return hex(bits)
    
    prior_bits_bytes = getBlock(block_id=previous_block).get('bits').to_bytes(4, byteorder = 'big')
    
    if (previous_block) % difficulty_adjustment_blocks != 0:
        #bits = getPriorBlock()[1]
        bits_bytes = prior_bits_bytes
        
    else:
        #previous_target = int.from_bytes(getTargetFromBits(prior_bits_bytes), 'big')
        start_bitcoin_height = getBlock(previous_block - 2015).get('bitcoin_block_height')
        end_bitcoin_height = getBlock(previous_block).get('bitcoin_block_height')
        new_target = getRetarget( start_bitcoin_height, end_bitcoin_height, target_timespan_bitcoin_blocks, prior_bits_bytes)
        bits_bytes = int(getBitsFromTarget(new_target),0).to_bytes(4,'big')
    
    #bits_bytes = bits.to_bytes(4, byteorder = 'big')
    
    return bits_bytes


def getRetarget(start_bitcoin_height, end_bitcoin_height, target_bitcoin_blocks, prior_bits):
#difficulty is tied to trying to make the blocks line up with bitcoin blocks
    
    block_timespan = end_bitcoin_height - start_bitcoin_height
    adjustment = block_timespan / target_bitcoin_blocks 
    
    #like bitcoin, max difficulty change is factor of 4
    adjustment = max(min(adjustment,4),0.25)
    
    previous_target = int.from_bytes(getTargetFromBits(prior_bits), 'big')
    
    new_target = round(previous_target*adjustment)
    max_target = int.from_bytes(getTargetFromBits(starting_bits), 'big')
    
    #like bitcoin, target is not allowed to exceed the initial one
    new_target = min(new_target,max_target)
    
    return new_target


if __name__ == '__main__':
    
    print(getBitsCurrentBlock())
    
    print(getRetarget(1000, 2000, 1000, 0x1d00ffff.to_bytes(4,byteorder='big')))


