'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queue_new_transaction_from_peer
from wallet.transaction_creation import createSimpleTransactionTransfer
from binascii import hexlify
from node.blockchain.transaction_operations import validateMempoolTransaction
import socket

def broadcastTransaction(transaction):
    
    queue_new_transaction_from_peer(transaction, threaded=False)

    return True


if __name__ == '__main__':

    '''
    select 
    '["' || pub_key || '","' || private_key || '","' || st_astext(geom) || '",' || planet_id::varchar || ',' || vout::varchar || ',"' || transaction_hash || '"]',
        block_id
    from bitland.utxo u
    join wallet.addresses a on u.pub_key = a.public_key 
    order by block_id desc
    '''
    
    inputs = ["56541e1d325c8751fc3e38cb40a6d94fd5ebf4bc9093c648d7d97bfdc4154f7b34468c80847675adbd381900ec93b0ae216b044251078e3c0cda25671ca21ab2","ca1728e736aaf3b4ca51ffc5100137cf36b8f746d4280934d1fe677c062d0c84","POLYGON((-83.671875 78.44544,-83.671875 78.2199,-84.375 78.2199,-84.375 78.44544,-83.671875 78.44544))",1,0,"7841dcc6e399023e1235f384997043c76abf9a1a0ccfb663be7881261d34f896"]
    
    input_public_key = inputs[0]
    input_private_key = inputs[1]
    polygon = inputs[2]
    planet_id = inputs[3]
    vout = inputs[4]
    input_transaction_hash = inputs[5]
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    transaction_hex = hexlify(simple_transaction).decode('utf-8')
    
    x = broadcastTransaction(transaction_hex)

    