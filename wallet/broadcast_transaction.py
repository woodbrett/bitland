'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queue_new_transaction_from_peer
from wallet.create_transaction_simple import createSimpleTransactionTransfer
from binascii import hexlify
from node.blockchain.transaction_operations import validateMempoolTransaction


def broadcast_transaction(transaction):
    
    queue_new_transaction_from_peer(transaction,threaded=False)

    return True


if __name__ == '__main__':

    input_public_key = '0fcc5c84f971522179472d1dd1e9063acc90d6787d5f01c1aafd44ae640062396b263aa7c8ab59163f375d1cd161f4f7e9a8d724a8905a3db84aa1b3e8a743a9'
    input_private_key = '279f87d4961ff7f607b38f6c70197b34453b4656207c2b3de3a8732213a8f357'
    polygon = 'POLYGON ((-50.625 86.0697, -50.625 85.90662, -53.4375 85.90662, -53.4375 86.0697, -50.625 86.0697))'
    planet_id = 1
    vout = 0
    input_transaction_hash = '4dd77f5b032bd8c8d37a633eb82b8e04bb077cb86a1a101e45174e0eee279027'
    
    simple_transaction = createSimpleTransactionTransfer(input_transaction_hash, vout, input_private_key, input_public_key, polygon, planet_id)
    transaction_hex = hexlify(simple_transaction).decode('utf-8')
    
    x = broadcast_transaction(transaction_hex)
    
    #print(validateMempoolTransaction(simple_transaction))