'''
Created on Mar 6, 2021

@author: brett_wood
'''
import requests
from system_variables import (
    transaction_validation_url,
    block_height_url,
    rpc_user,
    rpc_password,
    node_url,
    get_block_by_hash_url,
    bitcoin_source
    )
from _sha256 import sha256
import base58
from binascii import unhexlify, hexlify
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from utilities.bitcoin.bitcoin_requests_node import getCurrentBitcoinBlockHeightNode,\
    getBlockHeightFromHashNode, getBestBlockHashNode, getLastXBitcoinHashesNode,\
    validateBitcoinAddressNode, getOutputListBlockNode,\
    getBlockHashFromHeightNode
from utilities.bitcoin.bitcoin_requests_external import getCurrentBitcoinBlockHeightExternal,\
    getBlockHeightFromHashExternal, getBestBlockHashExternal,\
    getLastXBitcoinHashesExternal, validateBitcoinAddressExternal,\
    getOutputListBlockExternal, getBlockHashFromHeightExternal


def getCurrentBitcoinBlockHeight(bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source
    
    if bitcoin_source_request == 'local_node':
        return getCurrentBitcoinBlockHeightNode()
    
    elif bitcoin_source_request == 'blockstream_api':
        return getCurrentBitcoinBlockHeightExternal()
     
    else:
        return None


def getBlockHeightFromHash(bitcoin_hash,bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source
    
    if bitcoin_source_request == 'local_node':
        return getBlockHeightFromHashNode(bitcoin_hash)
    
    elif bitcoin_source_request == 'blockstream_api':
        return getBlockHeightFromHashExternal(bitcoin_hash)
     
    else:
        return None


def getBlockHashFromHeight(bitcoin_height, bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source
    
    if bitcoin_source_request == 'local_node':
        return getBlockHashFromHeightNode(bitcoin_height)
    
    elif bitcoin_source_request == 'blockstream_api':
        return getBlockHashFromHeightExternal(bitcoin_height)
     
    else:
        return None


def getBestBlockHash(bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source

    if bitcoin_source_request == 'local_node':
        return getBestBlockHashNode()
    
    elif bitcoin_source_request == 'blockstream_api':
        return getBestBlockHashExternal()
     
    else:
        return None


def getLastXBitcoinHashes(x, block_height=None, bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source

    if bitcoin_source_request == 'local_node':
        return getLastXBitcoinHashesNode(x, block_height)
    
    elif bitcoin_source_request == 'blockstream_api':
        return getLastXBitcoinHashesExternal(x, block_height)
     
    else:
        return None
    
    
def getValidateBitcoinAddress(address_string, bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source

    if bitcoin_source_request == 'local_node':
        return validateBitcoinAddressNode(address_string)
    
    elif bitcoin_source_request == 'blockstream_api':
        return validateBitcoinAddressExternal(address_string)
     
    else:
        return None


def getOutputListBlock(block_height=None, bitcoin_source_request=None):
    
    if bitcoin_source_request == None:
        bitcoin_source_request = bitcoin_source
    
    if bitcoin_source_request == 'local_node':
        return getOutputListBlockNode(block_height)
    
    elif bitcoin_source_request == 'blockstream_api':
        return getOutputListBlockExternal(block_height)
     
    else:
        return None    



if __name__ == '__main__':
    
    '''
    # rpc_user and rpc_password are set in the bitcoin.conf file
    rpc_connection = AuthServiceProxy("http://%s:%s@192.168.86.34:8332"%(rpc_user, rpc_password))
    best_block_hash = rpc_connection.getbestblockhash()
    print(rpc_connection.getblock(best_block_hash))
    
    # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    commands = [ [ "getblockhash", height] for height in range(100) ]
    block_hashes = rpc_connection.batch_(commands)
    blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
    block_times = [ block["time"] for block in blocks ]
    print(block_times)   
    
    commands = [ [ "getblockhash", height] for height in range(30,20) ]
    block_hashes = rpc_connection.batch_(commands)
    print(block_hashes)
    blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
    block_heights = [ block["height"] for block in blocks ]
    print(block_heights)     
    '''
    
    
    
    hash = '0000000000000000000976cd2fec95bfaf889a7c3d434f9520b30db26f25c3fc'
    #hash = '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
    address = get_block_by_hash_url.replace(':hash', hash)
    print(address)
    block = requests.get(address).content
    print(block[0:100])
    
    print(hexlify(block))
    
    #rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    #block_node = rpc_connection.getblock(hash,2)
    #print(block_node)

    parseBlockFile(block)