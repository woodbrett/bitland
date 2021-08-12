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
    
    transaction_hex = '000201034f651474a9f41af5b7d480afdd8ec65730eaaf1872009be993b829a7d69e6bd400000103010057504f4c59474f4e28282d32322e352038382e39373230322c2d32322e352038382e38323239382c2d33332e37352038382e38323239382c2d33332e37352038382e39373230322c2d32322e352038382e39373230322929405aaf412f897550d8e2dfc014dcd8b907374d50828dbaaba41f8deccfe7cfaa9e52522d40ef765999ea1ae2917d462d317fb709ebcdbbfff7997787d0e03357ae000000002af8015e000000000000000000'    
    x = broadcastTransaction(transaction_hex, use_threading=False)









