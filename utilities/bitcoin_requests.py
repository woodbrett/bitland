'''
Created on Mar 6, 2021

@author: brett_wood
'''
import requests
from system_variables import *

def getCurrentBitcoinBlockHeight():
    calculated_block_height = int(requests.get(block_height_url).text)
    return calculated_block_height


