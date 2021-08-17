'''
Created on Dec 1, 2020

@author: brett_wood
'''
import struct
from codecs import decode, encode
from binascii import hexlify, unhexlify
from utilities.serialization import deserialize_text, serialize_text
from utilities.sql_utils import executeSql
from wallet.key_generation import *
import ecdsa

def serializeTransaction(version, inputs, outputs, contingencies):
        
    input_count_num = len(inputs)
    input_count = input_count_num.to_bytes(1, byteorder = 'big')
    
    serialized_transaction = version + input_count
    
    for i in range(0, input_count_num):
    
        input_version = inputs[i][0]
        transaction_id = inputs[i][1]
        vout = inputs[i][2]
        signature = inputs[i][3]
        sig_length = len(signature).to_bytes(1, byteorder = 'big')
        
        inputs_appended = (input_version + transaction_id + vout + sig_length + signature)
        
        serialized_transaction = serialized_transaction + inputs_appended
    
    output_count_num = len(outputs)
    output_count = output_count_num.to_bytes(1, byteorder = 'big')

    serialized_transaction = serialized_transaction + output_count
    
    for i in range(0, output_count_num):
        
        output_version = outputs[i][0]
        planet = outputs[i][1]
        shape = outputs[i][2]
        shape_length = len(shape).to_bytes(2, byteorder = 'big')
        public_script = outputs[i][3]
        public_script_length = len(public_script).to_bytes(1, byteorder = 'big')
        
        outputs_appended = (output_version + planet + shape_length + shape + public_script_length + public_script)
                
        serialized_transaction = serialized_transaction + outputs_appended
        
    #contingencies logic 
    miner_fee_sats = contingencies[0]
    miner_fee_blocks = contingencies[1]
    transfer_fee_sats = contingencies[2]
    transfer_fee_blocks = contingencies[3]
    transfer_fee_address = contingencies[4]
    transfer_fee_address_length = len(transfer_fee_address).to_bytes(1, byteorder = 'big')
    
    serialized_transaction = serialized_transaction + miner_fee_sats + miner_fee_blocks + transfer_fee_sats + transfer_fee_blocks + transfer_fee_address_length + transfer_fee_address
        
    return serialized_transaction;


def deserializeTransaction(transaction, start_pos=0):
    
    counter = start_pos
    version_bytes = 2
    input_count_bytes = 1
    input_version_bytes = 1
    input_transaction_bytes = 32
    input_vout_bytes = 1
    sig_length_bytes = 1
    
    output_count_bytes = 1
    output_version_bytes = 1
    planet_bytes = 1
    shape_length_bytes = 2
    public_script_length_bytes = 1
    miner_fee_sats_bytes = 6
    miner_fee_blocks_bytes = 2
    transfer_fee_sats_bytes = 6
    transfer_fee_blocks_bytes = 2
    transfer_fee_address_length_bytes = 1
    
    version = transaction[counter:(counter + version_bytes)]
    counter = counter + version_bytes
    
    input_count = transaction[counter:(counter + input_count_bytes)]
    counter = counter + input_count_bytes
    input_count_int = int.from_bytes(input_count, byteorder='big')
    
    input_transactions = []
    
    for i in range(0, input_count_int):

        input_transaction = []
        
        input_version = transaction[counter:(counter + input_version_bytes)]
        input_transaction.append(input_version)
        counter = counter + input_version_bytes
        
        transaction_id = transaction[counter:(counter + input_transaction_bytes)]
        input_transaction.append(transaction_id)
        counter = counter + input_transaction_bytes
        
        vout = transaction[counter:(counter + input_vout_bytes)]
        input_transaction.append(vout)
        counter = counter + input_vout_bytes
        
        sig_bytes = int.from_bytes(transaction[counter:(counter + sig_length_bytes)], byteorder='big')
        counter = counter + sig_length_bytes
        
        signature = transaction[counter:(counter + sig_bytes)]
        input_transaction.append(signature)
        counter = counter + sig_bytes
        
        input_transactions.append(input_transaction)
    
    output_count = transaction[counter:(counter + output_count_bytes)]
    counter = counter + output_count_bytes
    output_count_int = int.from_bytes(output_count, byteorder='big')
    
    output_transactions = []
    
    for i in range(0, output_count_int):
        
        output_transaction = []
        
        output_version = transaction[counter:(counter + output_version_bytes)]
        output_transaction.append(output_version)
        counter = counter + output_version_bytes
        
        planet_id = transaction[counter:(counter + planet_bytes)]
        output_transaction.append(planet_id)
        counter = counter + planet_bytes
        
        shape_bytes = transaction[counter:(counter + shape_length_bytes)]
        counter = counter + shape_length_bytes
        shape_bytes_num = int.from_bytes(shape_bytes, byteorder='big')
        
        shape = transaction[counter:(counter + shape_bytes_num)]
        output_transaction.append(shape)
        counter = counter + shape_bytes_num
        
        public_script_bytes = transaction[counter:(counter + public_script_length_bytes)]
        counter = counter + public_script_length_bytes
        public_script_bytes_num = int.from_bytes(public_script_bytes, byteorder='big')
        
        public_script = transaction[counter:(counter + public_script_bytes_num)]
        output_transaction.append(public_script)
        counter = counter + public_script_bytes_num
        
        output_transactions.append(output_transaction)
        
    #contingencies logic
    miner_fee_sats = transaction[counter:(counter + miner_fee_sats_bytes)]
    counter = counter + miner_fee_sats_bytes

    miner_fee_blocks = transaction[counter:(counter + miner_fee_blocks_bytes)]
    counter = counter + miner_fee_blocks_bytes
    
    transfer_fee_sats = transaction[counter:(counter + transfer_fee_sats_bytes)]
    counter = counter + transfer_fee_sats_bytes
    
    transfer_fee_blocks = transaction[counter:(counter + transfer_fee_blocks_bytes)]
    counter = counter + transfer_fee_blocks_bytes
    
    transfer_fee_address_length = int.from_bytes(transaction[counter:(counter + transfer_fee_address_length_bytes)],'big')
    counter = counter + transfer_fee_address_length_bytes

    transfer_fee_address = transaction[counter:(counter + transfer_fee_address_length)]
    counter = counter + transfer_fee_address_length

    contingencies = [miner_fee_sats,miner_fee_blocks,transfer_fee_sats,transfer_fee_blocks,transfer_fee_address]
    
    return(version, input_transactions, output_transactions, contingencies, counter)


    
    
        