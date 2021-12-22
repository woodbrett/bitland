'''
Created on Oct 3, 2021

@author: admin
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


def getCurrentBitcoinBlockHeightNode():

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    calculated_block_height = rpc_connection.getblockcount()
    return calculated_block_height
    

def getBlockHeightFromHashNode(bitcoin_hash):
    
    try:
        rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
        block_height = rpc_connection.getblockheader(bitcoin_hash).get('height')
    
    except:
        block_height = 'no_block_found'
    
    return block_height


def getBlockHashFromHeightNode(block_height):
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    block_hash = rpc_connection.getblockhash(block_height)
    return block_hash


def getBestBlockHashNode():
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    best_block_hash = rpc_connection.getbestblockhash()
    return best_block_hash


def getLastXBitcoinHashesNode(x, block_height=None):
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))

    if block_height == None:
        block_height = rpc_connection.getblockcount()

    commands = [ [ "getblockhash", height] for height in range(block_height - x + 1,block_height + 1) ]
    block_hashes = rpc_connection.batch_(commands)    
    
    return block_hashes


def validateBitcoinAddressNode(address_string):

    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    
    return rpc_connection.validateaddress(address_string).get('isvalid')


def getOutputListBlockNode(block_height):
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(rpc_user, rpc_password, node_url))
    block_hash = rpc_connection.getblockhash(block_height)
    bitcoin_block = rpc_connection.getblock(block_hash, 2)
    
    transactions = bitcoin_block.get('tx')
    address_value_array = []
    
    for i in range(0,len(transactions)):
        transaction_vout = transactions[i].get('vout')
        txid = transactions[i].get('txid')
        for j in range(0,len(transaction_vout)):
            value = transaction_vout[j].get('value') * 100000000
            addresses = transaction_vout[j].get('scriptPubKey').get('addresses')
            type = transaction_vout[j].get('scriptPubKey').get('type')
            if addresses != None and len(addresses) == 1 and type == 'pubkeyhash':
                address = addresses[0]
                address_value_array.append([txid, address,value])
    
    return address_value_array


if __name__ == '__main__':

    print(getCurrentBitcoinBlockHeightNode())
    
    