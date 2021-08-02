'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queue_new_transaction_from_peer
from wallet.transaction_creation import createSimpleTransactionTransfer
from binascii import hexlify, unhexlify
from node.blockchain.transaction_operations import validateMempoolTransaction
import socket
from node.blockchain.transaction_serialization import deserialize_transaction

def broadcastTransaction(transaction, use_threading=True):
    
    queue_new_transaction_from_peer(transaction, use_threading)

    return True


if __name__ == '__main__':
    
    transaction_hex = '00020101a8788b7873e8c5671d62c2f3936b34ec3207bfc68062ea4250e4b10182dd88450240267fc4fc307f232dca71cd152b2dc00d929559f55b6c302e5560c5cdabf5cd5e748030642614468fe4d4ddc43be3cd04ac9269201eedfee0fbb5faca114a41f0010101007e504f4c59474f4e28282d36302e3338323136352038342e34313839322c2d36302e34363837352038342e34313839322c2d36302e34363837352038342e363538352c2d36302e34363837352038342e39303934322c2d36302e3336333035352038342e39303934322c2d36302e3338323136352038342e3431383932292940efbcba90267a9f48bc28b7e817c082b8862253204f40f567146424a8fd9657d89003821bb0aaa990081a2a07e31fad2a93238bcce0e4c720a5017ce005c334ff0000000000000000000000000000000000'    
    x = broadcastTransaction(transaction_hex, use_threading=False)









