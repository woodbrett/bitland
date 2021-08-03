'''
Created on Jul 23, 2021

@author: brett_wood
'''
from binascii import hexlify, unhexlify
from _codecs import decode


mining_path = 'MULTILINESTRING ((-24.32582123586823 89.84080925775434, -74.62860694880915 82.52182923327297, -91.10241210722151 75.38399911209015, -95.0423241796008 66.86026257852093, -100.6851598368639 54.57263922226819),(-101.3573454825694 55.02763381008007, -82.54937943634791 31.48094731046708),(-99.09477782473776 54.17424604757469, -110.205550984981 30.49451859774517, -96.77412063206563 28.15864596136793))'

if __name__ == "__main__":

    miner_bitcoin_address = '15NwUktZt4kWMLqK5QLrxAMQapyeFxAi6h'
    miner_bitcoin_address_bytes = hexlify(miner_bitcoin_address.encode('utf-8'))
    
    print(unhexlify(miner_bitcoin_address_bytes))

    transfer_fee_address_1 = '1GX28yLjVWux7ws4UQ9FB4MnLH4UKTPK2z'
    hexlify(transfer_fee_address_1.encode('utf-8')).decode('utf-8')
    
    x = b'31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668'
    print(x.decode('utf-8'))
    
    print(unhexlify('31354e77556b745a74346b574d4c714b35514c7278414d5161707965467841693668').decode('utf-8'))