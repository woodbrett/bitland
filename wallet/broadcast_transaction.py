'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queue_new_transaction_from_peer
from wallet.create_transaction_simple import createSimpleTransactionTransfer
from binascii import hexlify
from node.blockchain.transaction_operations import validateMempoolTransaction


def broadcast_transaction(transaction):
    
    queue_new_transaction_from_peer(transaction)

    return True


if __name__ == '__main__':

    input_public_key = '3bc16bd3f696e736cda684f2ab831c759d237025d92789f0139e1c0e87cad170c78e4d992fe63e49e9f82822a549d5210fbcd32c490791b083833cb54007227f'
    input_private_key = 'ee706f0ad2a53f7eb8f6f0b35b9af6dec481af2c781f54c91da8d5dee6c80af1'
    polygon = 'POLYGON ((-47.8125 86.60538, -47.8125 86.418, -50.625 86.418, -50.625 86.60538, -47.8125 86.60538))'
    planet_id = 1
    vout = 0
    input_transaction_hash = 'c4a1a627ebf4994e7aa3c6544c2614f5eb5d55c52c84d3b1f4384ee5531bd883'
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    transaction_hex = hexlify(simple_transaction).decode('utf-8')
    
    x = broadcast_transaction(transaction_hex)
    
    #print(validateMempoolTransaction(simple_transaction))
    