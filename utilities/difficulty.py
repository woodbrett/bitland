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
from node.blockchain.queries import (
    getPriorBlock,
    getMaxBlock,
    getBlockById)
from node.information.blocks import (
    getBlockInformation
    )

def get_bits_from_target(target):
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


def get_target_from_bits(bits):
    
    bits_int = int.from_bytes(bits, byteorder='big')
    
    exp = bits_int >> 24
    mant = bits_int & 0xffffff
    target_hexstr = '%064x' % (mant * (1<<(8*(exp - 3))))
    target_bytes = decode(target_hexstr, "hex")
    
    return target_bytes


def get_bits_current_block():
    
    previous_block = getMaxBlock()
    
    if previous_block == 0:
        bits = starting_bits #0x1d00ffff
        return bits
        #return hex(bits)
        
    if (previous_block) % difficulty_adjustment_blocks != 0:
        bits = getPriorBlock()[1]
        
    else:
        previous_target = get_target_from_bits(bits)
        adjustment = get_difficulty_adjustment( previous_block - 2016, previous_block)
        bits = previous_target * adjustment
    
    bits_bytes = bits.to_bytes(4, byteorder = 'big')
    
    return bits_bytes


def get_difficulty_adjustment(start_block, end_block):
#difficulty is tied to trying to make the blocks line up with bitcoin blocks
    
    block_timespan = getBlockInformation(end_block).bitcoin_block_height - getBlockInformation(start_block).bitcoin_block_height
    adjustment = target_timespan_bitcoin_blocks / block_timespan
    
    return adjustment


if __name__ == '__main__':
    
    difficulty = '0000000ffff00000000000000000000000000000000000000000000000000000'
    dif_int = unhexlify(difficulty)
    print(dif_int)
    
    print(get_bits_from_target(431352564656180951890503621515583861376174379817186625378204369551360))
    
    bits = 0x1d00ffff
    bits_bytes = bits.to_bytes(4, byteorder = 'big')
    
    print(get_target_from_bits(bits_bytes))
        
    print(get_bits_current_block())
    
    print(0 % 2016 != 0)
    
    
    