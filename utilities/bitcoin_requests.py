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

