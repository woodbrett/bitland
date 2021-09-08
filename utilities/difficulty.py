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
    #print(type(target))
    #print(type(size))
    #print(size)
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
        
    if (previous_block) % difficulty_adjustment_blocks != 0:
        bits = getPriorBlock()[1]
        
    else:
        previous_target = getTargetFromBits(bits)
        adjustment = getDifficultyAdjustment( previous_block - 2016, previous_block)
        bits = previous_target * adjustment
    
    bits_bytes = bits.to_bytes(4, byteorder = 'big')
    
    return bits_bytes


def getDifficultyAdjustment(start_block, end_block):
#difficulty is tied to trying to make the blocks line up with bitcoin blocks
    
    block_timespan = getBlock(end_block).get('bitcoin_block_height') - getBlock(start_block).get('bitcoin_block_height')
    adjustment = target_timespan_bitcoin_blocks / block_timespan
    
    return adjustment


if __name__ == '__main__':
    
    difficulty = '0000000ffff00000000000000000000000000000000000000000000000000000'
    dif_int = unhexlify(difficulty)
    print(dif_int)
    
    print(getBitsFromTarget(431352564656180951890503621515583861376174379817186625378204369551360))
    
    bits = 0x1d00ffff
    bits_bytes = bits.to_bytes(4, byteorder = 'big')
    
    print(getTargetFromBits(bits_bytes))
        
    print(getBitsCurrentBlock())
    
    print(0 % 2016 != 0)
    
    
    