'''
Created on Jul 20, 2021

@author: brett_wood
'''
from node.networking.node_update_functions import queueNewTransactionFromPeer
from wallet.transaction_creation import createSimpleTransactionTransfer
from binascii import hexlify, unhexlify
from node.blockchain.transaction_operations import validateMempoolTransaction
import socket
from node.blockchain.transaction_serialization import deserialize_transaction

def broadcastTransaction(transaction, use_threading=True):
    
    queueNewTransactionFromPeer(transaction, use_threading)

    return True


if __name__ == '__main__':
    
    transaction_hex = '0002010311e0177991e5b50d90c1e3492c5d8b2cae1fa2c1d0fdd856a96458682f859cfa00000101010063504f4c59474f4e28282d39352e3632352036352e30313239342c2d39352e3632352036342e373937332c2d39352e3937363536332036342e373937332c2d39352e3937363536332036352e30313239342c2d39352e3632352036352e30313239342929406e0f1186ee6f4f60cfe515f196a3f365fd7e4befb858531bf6027eda43e1927fc333c9e0eb4e804cdddd64c40bd96a11d91c39267038b8cc6e74985b13fa27fe00000000271001f4000000000000000000'    
    x = broadcastTransaction(transaction_hex, use_threading=False)









