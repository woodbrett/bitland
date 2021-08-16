'''
Created on Nov 27, 2020

@author: brett_wood
'''
from binascii import unhexlify, hexlify

global starting_bits 
global difficulty_adjustment_blocks
global target_timespan_bitcoin_blocks
global genesis_prev_block
global contingency_validation_blocks
global claim_required_percentage_increase
global claim_blocks
global max_headers_send
global bitland_version

starting_bits_hex = 0x1d0ffff0  # original was 0x1d00ffff
starting_bits = starting_bits_hex.to_bytes(4, 'big')
difficulty_adjustment_blocks = 2016

target_timespan_bitcoin_blocks = 2016
genesis_prev_block = unhexlify('0000000000000000000000000000000000000000000000000000000000000000')

contingency_validation_blocks = 10

claim_required_percentage_increase = 0.5
claim_blocks = 20  # number of blocks from when a claim is made until it wins the land, 1 years
max_headers_send = 2000

bitland_version = 1

bitcoin_block_range = 6 #when validating a new block coming in, the bitcoin block it has in header has to be within this many of the node's calculated bitcoin block height