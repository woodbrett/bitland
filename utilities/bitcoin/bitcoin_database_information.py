'''
Created on Oct 4, 2021

@author: admin
'''
from utilities.sql_utils import *


def getLastXBitcoinBlocksDb(x, block_height=None):
    
    if block_height != None:
        select = 'select block_height , block_hash from bitcoin.block where block_height <= ' + str(block_height) + ' order by block_height desc limit ' + str(x) + ';'
        
    else:
        select = 'select block_height , block_hash from bitcoin.block order by block_height desc limit ' + str(x) + ';'
    
    return executeSqlMultipleRows(select)


if __name__ == '__main__':
    
    print(getLastXBitcoinBlocksDb(64))