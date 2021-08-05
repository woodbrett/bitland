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
    
    transaction_hex = '0002010311e0177991e5b50d90c1e3492c5d8b2cae1fa2c1d0fdd856a96458682f859cfa00000103010063504f4c59474f4e28282d39352e3632352036352e30313239342c2d39352e3632352036342e373937332c2d39352e3937363536332036342e373937332c2d39352e3937363536332036352e30313239342c2d39352e3632352036352e30313239342929406e011056af36ce04d4f3f04cb0bafa8babebb1ecf36788fce75d6f4c5d5593479e3a7c3ce7919724f901e2e6b3f787a99cf2575458f29d5c3ccd5e574f1df37f0000000088b8015e000000000000000000'    
    x = broadcastTransaction(transaction_hex, use_threading=False)









