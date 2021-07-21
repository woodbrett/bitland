'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queue_new_transaction_from_peer
from wallet.create_transaction_simple import createSimpleTransactionTransfer
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
    
    '''
    inputs = ["4055aba9fdc64318b585a41fe66a1101efeec0d5f7794dea2a55df356e9deea1597c4e00eea023122f98e1c5b9fbea2ee02b19973cd442e10d7dbe526753b251","7b7442d3622f3c48d005f45680385d5dafe383f0662f523bb3d184e9f7900042","POLYGON((-28.125 88.69068,-28.125 88.461,-33.75 88.461,-33.75 88.69068,-28.125 88.69068))",1,0,"46da56ee09a208af6badf28fe8a4bdb300c651ab270980c0fe4d7dcb804a57ae"]
    
    input_public_key = inputs[0]
    input_private_key = inputs[1]
    polygon = inputs[2]
    planet_id = inputs[3]
    vout = inputs[4]
    input_transaction_hash = inputs[5]
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    transaction_hex = hexlify(simple_transaction).decode('utf-8')
    
    x = broadcastTransaction(transaction_hex)
    '''
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(hostname)
    print(local_ip)
    
    
    