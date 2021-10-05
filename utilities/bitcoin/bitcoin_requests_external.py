'''
Created on Oct 3, 2021

@author: admin
'''
import requests
from system_variables import (
    transaction_validation_url,
    block_height_url,
    get_block_by_hash_url,
    get_block_hash_by_height_url,
    block_hash_tip_url,
    last_ten_block_hashes_url,
    get_block_height_by_hash_url
    )
from utilities.bitcoin_parser.block import Block
from utilities.bitcoin.bitcoin_requests_node import getOutputListBlockNode,\
    getLastXBitcoinHashesNode
import math
from utilities.bitcoin.bitcoin_database_information import getLastXBitcoinBlocksDb


def getCurrentBitcoinBlockHeightExternal():
    
    calculated_block_height = int(requests.get(block_height_url).text)
    return calculated_block_height


def getBlockHeightFromHashExternal(bitcoin_hash):
    
    url = get_block_height_by_hash_url.replace(':hash', str(bitcoin_hash))
    block_info = requests.get(url).json()
    
    return block_info.get('height')


def getBlockHashFromHeightExternal(block_height):
    
    hash_address = get_block_hash_by_height_url.replace(':height', str(block_height))
    block_hash = requests.get(hash_address).text
    return block_hash


def getBestBlockHashExternal():
    
    best_block_hash = requests.get(block_hash_tip_url).text
    return best_block_hash


#UPDATE
def getLastXBitcoinHashesExternal(x, block_height=None):
    
    #there were too many calls going to the external API so instead will reference the database
    '''
    if block_height == None:
        block_height = getCurrentBitcoinBlockHeightExternal()
    
    target = block_height - x
    analysis_height = block_height 
    hashes = []
    
    while analysis_height > target:
        url = last_ten_block_hashes_url.replace(':height', str(analysis_height))
        blocks = requests.get(url).json()
        for i in range(0,len(blocks)):
            if len(hashes) < x:
                hashes.insert(0,blocks[i].get('id'))
        
        analysis_height = blocks[-1].get('height') - 1
    
    return hashes
    '''
    
    blocks = getLastXBitcoinBlocksDb(x, block_height)
    
    '''
    if len(blocks) != x and block_height != None:
        synchWithBitcoin(block_height - x, block_height)
        blocks = getLastXBitcoinBlocksDb(x, block_height)
    '''
     
    if len(blocks) != x:
        print('cant calculate last x blocks, block count doesnt line up in database')
        return None
    
    for i in range(0,len(blocks)-1):
        block_i = blocks[i][0]
        block_i_plus = blocks[i+1][0]
        if blocks[i][0] != (blocks[i+1][0] + 1):
            print('cant calculate last x blocks, block sequence off in database')
            return None
    
    hashes = [item[1] for item in blocks]
    hashes = hashes[::-1]
    
    return hashes
    

#UPDATE - too many calls going to external API, maybe we just have to put the bitcoin address validation logic inside bitland
def validateBitcoinAddressExternal(address_string):

    '''
    transaction_validation_url_sub = transaction_validation_url.replace(':address', address_utf8)
    print(transaction_validation_url_sub)
    
    r = requests.get(transaction_validation_url_sub)
    
    try:
        address_info = r.json()
        return True
        
    except Exception:
        address_info = r.text
        return False
    '''

    return True


def getOutputListBlockExternal(block_height):

    hash_address = get_block_hash_by_height_url.replace(':height', str(block_height))
    hash = requests.get(hash_address).text

    block_address = get_block_by_hash_url.replace(':hash', hash)
    block_raw = requests.get(block_address).content

    address_value_array = []
    block = Block(block_raw)
       
    for i in range (0,block.n_transactions):
        transaction = block.transactions[i]
        txid = transaction.txid
        for j in range (0,len(transaction.outputs)):
            output = transaction.outputs[j]
            value = output.value
            if output.addresses != None and len(output.addresses) == 1 and output.type == 'pubkeyhash':
                address = str(output.addresses[0])
                address_value_array.append([txid,address,value])
    
    return address_value_array


if __name__ == '__main__':
    
    best_hash = getBestBlockHashExternal()
    print(getBlockHeightFromHashExternal(best_hash))
    
    #x = getOutputListBlockExternal(200000)
    
    '''
    external = getOutputListBlockExternal(200000)
    #820
    
    node = getOutputListBlockNode(200000)
    #820
    
    for i in range(0,max(len(external),len(node))):
        print(str(i))
        print("external: " + str(external[i]))
        print("node: " + str(node[i]))
        print(external[i][0] == node[i][0])
        print(external[i][1] == node[i][1])
    '''
    
    #last x blocks
    print(getLastXBitcoinHashesNode(64, 703509))
    print(getLastXBitcoinHashesExternal(64, 703509))
        
    
    