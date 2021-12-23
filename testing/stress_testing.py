'''
Created on Dec 23, 2021

@author: admin
'''
from utilities.bitcoin.bitcoin_requests_external import validateBitcoinAddressExternal,\
    getLastXBitcoinHashesExternal, getCurrentBitcoinBlockHeightExternal,\
    getBlockHashFromHeightExternal, getOutputListBlockExternal
from documentation.system_variables import transaction_validation_url
import requests

def call_external_bitcoin_api_repeatedly(count):
    
    address = 'bc1qamgmd4s53pq5y0ejlnaps580yujpvyhvanvx2y'
    validate = validateBitcoinAddressExternal(address)
    print(validate)
    
    block_height = getCurrentBitcoinBlockHeightExternal()
    
    for i in range(0,count):
        
        address = 'bc1qamgmd4s53pq5y0ejlnaps580yujpvyhvanvx2y'
        transaction_validation_url_sub = transaction_validation_url.replace(':address', address)
        r = requests.get(transaction_validation_url_sub)
        
        validate = validateBitcoinAddressExternal(address)
        print(str(i) + ' ' + str(r.text))

        '''
        output_list = getOutputListBlockExternal(block_height)
        block_height = block_height - 1
        print(output_list[0:10])
        '''
        
    return True
    

if __name__ == '__main__':

    call_external_bitcoin_api_repeatedly(1000)