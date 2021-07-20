'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queue_new_transaction_from_peer
from wallet.create_transaction_simple import createSimpleTransactionTransfer
from binascii import hexlify
from node.blockchain.transaction_operations import validateMempoolTransaction


def broadcast_transaction(transaction):
    
    queue_new_transaction_from_peer(transaction, threaded=False)

    return True


if __name__ == '__main__':

    input_public_key = '24ac87325c1c45bdb82e6c767626e52853b324922632b1623ae41ec1a7f9587bc9b40c85b0203471262920d4b06342edaaffb21652394e82ce78ef34ddf6d1c1'
    input_private_key = '1446851f34a4e9658806678127c3c71973641673c4828f670b80d8aa1437ae66'
    polygon = 'POLYGON ((-74.53125 82.089, -74.53125 81.92502, -75.9375 81.92502, -75.9375 82.089, -74.53125 82.089))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '039d9da1d0f4dc09b442e5cf7323f653edf1f50ecf7c072958a6b19c90a0f567'
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    transaction_hex = hexlify(simple_transaction).decode('utf-8')
    
    x = broadcast_transaction(transaction_hex)
    
    