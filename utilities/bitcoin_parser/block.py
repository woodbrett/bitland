'''
Created on Oct 1, 2021

@author: admin
'''

# https://github.com/alecalve/python-bitcoin-blockchain-parser/tree/master/blockchain_parser

from utilities.bitcoin_parser.transaction import Transaction
from utilities.bitcoin_parser.block_header import BlockHeader
from utilities.bitcoin_parser.utils import format_hash, decode_varint, double_sha256
from binascii import hexlify
import requests
from system_variables import get_block_by_hash_url, get_block_hash_by_height_url


def get_block_transactions(raw_hex):
    """Given the raw hexadecimal representation of a block,
    yields the block's transactions
    """
    # Skipping the header
    transaction_data = raw_hex[80:]

    # Decoding the number of transactions, offset is the size of
    # the varint (1 to 9 bytes)
    n_transactions, offset = decode_varint(transaction_data)

    for i in range(n_transactions):
        # Try from 1024 (1KiB) -> 1073741824 (1GiB) slice widths
        for j in range(0, 20):
            try:
                offset_e = offset + (1024 * 2 ** j)
                transaction = Transaction.from_hex(
                    transaction_data[offset:offset_e])
                yield transaction
                break
            except:
                continue

        # Skipping to the next transaction
        offset += transaction.size


class Block(object):
    """
    Represents a Bitcoin block, contains its header and its transactions.
    """

    def __init__(self, raw_hex, height=None, blk_file=None):
        self.hex = raw_hex
        self._hash = None
        self._transactions = None
        self._header = None
        self._n_transactions = None
        self.size = len(raw_hex)
        self.height = height
        self.blk_file = blk_file

    def __repr__(self):
        return "Block(%s)" % self.hash

    @classmethod
    def from_hex(cls, raw_hex):
        """Builds a block object from its bytes representation"""
        return cls(raw_hex)

    @property
    def hash(self):
        """Returns the block's hash (double sha256 of its 80 bytes header"""
        if self._hash is None:
            self._hash = format_hash(double_sha256(self.hex[:80]))
        return self._hash

    @property
    def n_transactions(self):
        """Return the number of transactions contained in this block,
        it is faster to use this than to use len(block.transactions)
        as there's no need to parse all transactions to get this information
        """
        if self._n_transactions is None:
            self._n_transactions = decode_varint(self.hex[80:])[0]

        return self._n_transactions

    @property
    def transactions(self):
        """Returns a list of the block's transactions represented
        as Transaction objects"""
        if self._transactions is None:
            self._transactions = list(get_block_transactions(self.hex))

        return self._transactions

    @property
    def header(self):
        """Returns a BlockHeader object corresponding to this block"""
        if self._header is None:
            self._header = BlockHeader.from_hex(self.hex[:80])
        return self._header
    
    
if __name__ == '__main__':
    
    #0 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
    #1 00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048
    #x 0000000000000000000976cd2fec95bfaf889a7c3d434f9520b30db26f25c3fc

    hash_address = get_block_hash_by_height_url.replace(':height', str(697386))
    hash = requests.get(hash_address).text

    block_address = get_block_by_hash_url.replace(':hash', hash)
    block = requests.get(block_address).content
    print(block[0:100])
    
    print(hexlify(block[0:80]))

    block_hex = hexlify(block)
    
    x=get_block_transactions(block_hex)
        
    print(Block(block).transactions[0:2])
    print(len(Block(block).transactions))
    print(Block(block).hash)
    
    transaction0 = Block(block).transactions[0]
    
    print(transaction0.hash)
    print(transaction0.outputs)
    
    block = Block(block)
    
    for i in range (0,5):
        print('analyzing transaction ' + str(i))
        transaction = block.transactions[i]
        for j in range (0,len(transaction.outputs)):
            print('analyzing output ' + str(j))
            output = transaction.outputs[j]
            print(len(output.addresses))
            print(type(output.addresses))
            #print(output.addresses[0])
            print('value ' + str(output.value))
            print('addresses ' + str(output.addresses))
    