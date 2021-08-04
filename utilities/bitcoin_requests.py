'''
Created on Mar 6, 2021

@author: brett_wood
'''
import requests
from system_variables import (
    transaction_validation_url,
    block_height_url
    )
from _sha256 import sha256
import base58
from binascii import unhexlify, hexlify
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


def getCurrentBitcoinBlockHeight():
    calculated_block_height = int(requests.get(block_height_url).text)
    return calculated_block_height


def validateV1BitcoinAddress(address):

    base58Decoder = base58.b58decode(address).hex()
    prefixAndHash = base58Decoder[:len(base58Decoder)-8]
    checksum = base58Decoder[len(base58Decoder)-8:]
    
    hash = prefixAndHash
    for x in range(1,3):
        hash = sha256(unhexlify(hash)).hexdigest()
    
    y = hash[:8]
    
    is_valid = checksum == hash[:8]

    return is_valid


def validateBitcoinAddressFromBitcoinNode(address_utf8):
    
    rpc_user = 'admin'
    rpc_password = 'password'
    
    # rpc_user and rpc_password are set in the bitcoin.conf file
    rpc_connection = AuthServiceProxy("http://%s:%s@192.168.86.34:8332"%(rpc_user, rpc_password))
    
    return rpc_connection.validateaddress(address_utf8).get('isvalid')


def validateBitcoinAddressFromExternalAPI(address_utf8):
    
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
    
    rpc_user = 'admin'
    rpc_password = 'password'
    
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
    
    print(validateBitcoinAddressFromBitcoinNode('abc'))
    print(validateBitcoinAddressFromBitcoinNode('bc1qsdmlzvq79spjameemz5d8g2xfxxxgcp74h7j5w'))


