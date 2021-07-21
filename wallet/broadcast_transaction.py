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

    '''
    input_public_key = '24ac87325c1c45bdb82e6c767626e52853b324922632b1623ae41ec1a7f9587bc9b40c85b0203471262920d4b06342edaaffb21652394e82ce78ef34ddf6d1c1'
    input_private_key = '1446851f34a4e9658806678127c3c71973641673c4828f670b80d8aa1437ae66'
    polygon = 'POLYGON ((-74.53125 82.089, -74.53125 81.92502, -75.9375 81.92502, -75.9375 82.089, -74.53125 82.089))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '039d9da1d0f4dc09b442e5cf7323f653edf1f50ecf7c072958a6b19c90a0f567'
    '''
    
    '''
    select 
    '["' || pub_key || '","' || private_key || '","' || st_astext(geom) || '",' || planet_id::varchar || ',' || vout::varchar || ',"' || transaction_hash || '"]',
        block_id
    from bitland.utxo u
    join wallet.addresses a on u.pub_key = a.public_key 
    order by block_id desc
    '''
    
    inputs = ["5720ac9e0ae28a1920c7d42bb2dfc1c18662d5d4786283effedc784a6603dec6894ad8eca810af9926a127f978e3c8a4265c6a521954fa22a7737e3e2f8f8094","ba1a0b987d658f385d2a2d739b93820dc127fa822dccf6ccb2a5a6aa78d9c940","POLYGON((-81.5625 79.64586,-81.5625 79.39512,-82.265625 79.39512,-82.265625 79.64586,-81.5625 79.64586))",1,0,"541c89cea43e37cd372e74da2c80c57eff0dcdd4aa25cca31e479f7a5e1f6dca"]
    
    input_public_key = inputs[0]
    input_private_key = inputs[1]
    polygon = inputs[2]
    planet_id = inputs[3]
    vout = inputs[4]
    input_transaction_hash = inputs[5]
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    transaction_hex = hexlify(simple_transaction).decode('utf-8')
    
    x = broadcast_transaction(transaction_hex)
    
    
    
    