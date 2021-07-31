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
    
    transaction_hex = '0002010103aca220f7ec55e458acd9aafadc9af571da0676846fb6d5e2505c82a8849782004078708125ab06305a739e7ac4dbc7f0a3a571aad4976369069cf27469262b6f8650d0b508b73e36953f3b59934abc2ddad4ef5442114bae127d9efc49ba8810080101010051504f4c59474f4e28282d32322e352038392e37343637342c2d32322e352038392e35313836382c2d34352038392e35313836382c2d34352038392e37343637342c2d32322e352038392e373436373429294069022ccf1a0644a5e07eb2f89b3e9ab217fcc158f3525655a2a30f66c0c61a916858846f55db7172d5e71e3399d18fc191f0efc9b1fa12efcaeab17e0bbe27db0000000000000000000000000000000000'    
    x = broadcastTransaction(transaction_hex, use_threading=False)









