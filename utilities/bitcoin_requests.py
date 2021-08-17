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
    node_url 
    )
from _sha256 import sha256
import base58
from binascii import unhexlify, hexlify
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


def getCurrentBitcoinBlockHeight():
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    calculated_block_height = rpc_connection.getblockcount()
    return calculated_block_height


def getBlockHeightFromHash(bitcoin_hash):
    
    try:
        rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
        block_height = rpc_connection.getblockheader(bitcoin_hash).get('height')
    
    except:
        block_height = 'no_block_found'
    
    return block_height


def getBestBlockHash():
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    best_block_hash = rpc_connection.getbestblockhash()
    return best_block_hash


def getLastXBitcoinHashes(x, block_height=None):

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))

    if block_height == None:
        block_height = rpc_connection.getblockcount()

    commands = [ [ "getblockhash", height] for height in range(block_height - x + 1,block_height + 1) ]
    block_hashes = rpc_connection.batch_(commands)    
    
    return block_hashes


def validateBitcoinAddressFromBitcoinNode(address_utf8):

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    
    return rpc_connection.validateaddress(address_utf8).get('isvalid')


#OLD - node on the web
def validateV1BitcoinAddressExternalApi(address):

    base58Decoder = base58.b58decode(address).hex()
    prefixAndHash = base58Decoder[:len(base58Decoder)-8]
    checksum = base58Decoder[len(base58Decoder)-8:]
    
    hash = prefixAndHash
    for x in range(1,3):
        hash = sha256(unhexlify(hash)).hexdigest()
    
    y = hash[:8]
    
    is_valid = checksum == hash[:8]

    return is_valid


def getCurrentBitcoinBlockHeightExternalApi():
    calculated_block_height = int(requests.get(block_height_url).text)
    return calculated_block_height


def validateBitcoinAddressFromExternalApi(address_utf8):
    
    transaction_validation_url_sub = transaction_validation_url.replace(':address', address_utf8)
    print(transaction_validation_url_sub)
    
    r = requests.get(transaction_validation_url_sub)
    
    try:
        address_info = r.json()
        return True
        
    except Exception:
        address_info = r.text
        return False

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
    
    print(getBlockHeightFromHash('0000000000000000000fd641f66a7da2e7efd7c6a93b959ca59fa5d7809f6e71'))
    
    hashes = getLastXBitcoinHashes(64)
    print(len(hashes))
    print(hashes)

    
