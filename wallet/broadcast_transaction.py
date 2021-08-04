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
    
    transaction_hex = '0002010311e0177991e5b50d90c1e3492c5d8b2cae1fa2c1d0fdd856a96458682f859cfa00000103010063504f4c59474f4e28282d39352e3632352036352e30313239342c2d39352e3632352036342e373937332c2d39352e3937363536332036342e373937332c2d39352e3937363536332036352e30313239342c2d39352e3632352036352e3031323934292940cd4ce39c27dd3c9e356b2f343aae85395d13a754317594ebc6a438fc9d2c38d0be53afb36393851133b05faa6e0ceaeb5884aef2e752ef127a32ff55773e845b000000004e2001f4000000000000000000'    
    x = broadcastTransaction(transaction_hex, use_threading=False)









