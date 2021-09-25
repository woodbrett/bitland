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
        previous_target = hexlify(getTargetFromBits(prior_bits_bytes)).decode('utf-8')
        adjustment = getDifficultyAdjustment( previous_block - 2015, previous_block)
        new_target = previous_target * adjustment
        bits_bytes = getBitsFromTarget(new_target)
    
    #bits_bytes = bits.to_bytes(4, byteorder = 'big')
    
    return bits_bytes


def getDifficultyAdjustment(start_block, end_block):
#difficulty is tied to trying to make the blocks line up with bitcoin blocks
    
    #UPDATE cap up and down by factors of 4    
    block_timespan = getBlock(end_block).get('bitcoin_block_height') - getBlock(start_block).get('bitcoin_block_height')
    adjustment = target_timespan_bitcoin_blocks / block_timespan
    
    return adjustment


if __name__ == '__main__':
    
    print(0x0000000ffff00000000000000000000000000000000000000000000000000000)
    print(0x0000000ffff00000000000000000000000000000000000000000000000000000 * 0.33)
    print(0x0000000000000006770c3806960539ca83a24facbd99ea212f37f2a0e6a5629a)
    
    print(0x0000000ffff00000000000000000000000000000000000000000000000000000 / 0x00000000000404CB000000000000000000000000000000000000000000000000 )
    
    x = 0x0000000ffff00000000000000000000000000000000000000000000000000000 
    x = x * 4
    x = x / 3
    print(x)
    print(hex(x))
    
    bits = 424970034
    
     
    print(getBitsCurrentBlock())
    
    
    