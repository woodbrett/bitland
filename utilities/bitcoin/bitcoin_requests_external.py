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
import time


#UPDATE how it handles errors from, i used a very crude approach to start, tries it five times until it gets a response since sometimes it fails

def getCurrentBitcoinBlockHeightExternal():

    for i in range(0,5):
        response = requests.get(block_height_url)
        if response.status_code == 200:
            return int(response.text)
        time.sleep(5)
    
    return None


def getBlockHeightFromHashExternal(bitcoin_hash):
    
    url = get_block_height_by_hash_url.replace(':hash', str(bitcoin_hash))    
    
    for i in range(0,5):   
        response = requests.get(url)
        if response.status_code == 200 :
            return response.json().get('height')
        time.sleep(5)
        
    return None


def getBlockHashFromHeightExternal(block_height):
    
    hash_address = get_block_hash_by_height_url.replace(':height', str(block_height))
    
    for i in range(0,5): 
        response = requests.get(hash_address)
        if response.status_code == 200:
            return response.text
        time.sleep(5)
        
    return None


def getBestBlockHashExternal():
    
    for i in range(0,5): 
        response = requests.get(block_hash_tip_url)
        if response.status_code == 200:
            return response.text
        time.sleep(5)
        
    return None


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
    print(block_height)
    
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

    hash_address = 'https://blockstream.info/api/block-height/696703' #get_block_hash_by_height_url.replace(':height', str(block_height))
    for i in range(0,5): 
        response = requests.get(hash_address)
        if response.status_code == 200:
            hash = response.text
            break
        else:
            time.sleep(5)

    block_address = get_block_by_hash_url.replace(':hash', hash)
    for i in range(0,5): 
        response = requests.get(block_address)
        if response.status_code == 200:
            block_raw = response.content
            break
        else:
            time.sleep(5)

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
    
    print(getCurrentBitcoinBlockHeightExternal())
    #getOutputListBlockExternal(696703)
