'''
Created on Dec 1, 2020

@author: brett_wood
'''
import struct
from codecs import decode, encode
from binascii import hexlify, unhexlify
from utilities.serialization import deserialize_text, serialize_text
from utilities.sqlUtils import executeSql
from wallet.key_generation import *
import ecdsa

def serialize_transaction(version, inputs, outputs, contingencies):
        
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


def deserialize_transaction(transaction, start_pos=0):
    
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


if __name__ == '__main__':
    
    transaction_version = 2
    transaction_version = transaction_version.to_bytes(2, byteorder = 'big')
        
    #input 1 - standard
    type = 1 #standard
    transaction_hash = '89475fa839c308f2c52f7c088037544709a7075e9de1e7f16e47077ed824d645'
    vout = 0
    signature = 'd31c42f309a1e6742fe7efda401658f69221cb2ceec3fb8deb1ebe7db2117859a41ac4eb7a196cad3a3ddadacaccce4b9d967f7f60a839367a17628003a77397'
    input_1 = [type.to_bytes(1, byteorder = 'big'), unhexlify(transaction_hash), vout.to_bytes(1, byteorder = 'big'), unhexlify(signature)]
    
    #input 3 - claim
    type = 3 #claim
    transaction_hash = '89475fa839c308f2c52f7c088037544709a7075e9de1e7f16e47077ed824d645'
    vout = 0
    signature = ''
    input_2 = [type.to_bytes(1, byteorder = 'big'), unhexlify(transaction_hash), vout.to_bytes(1, byteorder = 'big'), unhexlify(signature)]
    
    inputs = [input_1,input_2]
    
    #output 1 - standard
    type = 1
    planet_id = 1
    coordinates = 'POLYGON ((-47.8125 86.418, -47.8125 86.2398, -50.625 86.2398, -50.625 86.418, -47.8125 86.418))'
    public_key = '8a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d616'
    output_1 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]
    
    #output 2 - collateral
    type = 2
    planet_id = 1
    coordinates = 'POLYGON ((-47.8125 86.418, -47.8125 86.2398, -50.625 86.2398, -50.625 86.418, -47.8125 86.418))'
    public_key = '8a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d616'
    output_2 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]
    
    #output 3 - claim
    type = 3
    planet_id = 1
    coordinates = 'POLYGON ((-47.8125 86.418, -47.8125 86.2398, -50.625 86.2398, -50.625 86.418, -47.8125 86.418))'
    public_key = '8a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d616'
    output_3 = [type.to_bytes(1, byteorder = 'big'), planet_id.to_bytes(1, byteorder = 'big'), coordinates.encode('utf-8'), unhexlify(public_key)]

    outputs = [output_1,output_2,output_3]

    #contingencies
    miner_fee_sats = 100000000000
    miner_fee_blocks = 12960 #12960 max
    transfer_fee_sats = 2000000000000
    transfer_fee_blocks = 1000 #12960 max
    transfer_fee_address = 'bc1q45wnsd3a2rz84jcp20u63y48w4frdchal6wssx'
    contingencies = [miner_fee_sats.to_bytes(6, byteorder = 'big'),
                     miner_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_sats.to_bytes(6, byteorder = 'big'),
                     transfer_fee_blocks.to_bytes(2, byteorder = 'big'),
                     transfer_fee_address.encode('utf-8')
                     ]

    serialized_transaction = serialize_transaction(transaction_version, inputs, outputs, contingencies)
    
    print(hexlify(serialized_transaction).decode('utf-8'))
    
    deserialized_transaction = deserialize_transaction(serialized_transaction)
    print(deserialized_transaction[0] == transaction_version)
    print(deserialized_transaction[1] == inputs)
    print(deserialized_transaction[2] == outputs)
    print(deserialized_transaction[3] == contingencies)
    
    test_landbase_1 = '0001000101010033504f4c59474f4e2828302039302c302038392e37343637342c2d39302038392e37343637342c2d39302039302c3020393029298038376333323339306138643631356634366564616361373133356234313939356138623138643532343664313231383762613763376563363532356435376139663639313461346161643466373530653230646535643530383439326366363338636530653631393939333364626131626664663630653266646236306466310000000000000000000000000000000000'
    test_transaction_2 = '000201383934373566613833396333303866326335326637633038383033373534343730396137303735653964653165376631366534373037376564383234643634350040bbb44c83cbf1ee5c2509f07ef4ec1bab3b067feaf91ea1da4c50a306402e3843f7ba1065f62743ec197570863a3f40103eef51fc8066814fb25805e5089199ce01015f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e34313829298035646636303634626631393031353563323432313362343134623561633462333338626631363065353066386662366564653264663066363338323161623364663536336463653234353530653165626436323336373632316535373138373137613165346361656532653031666261313633656337383139343434623666610000'
    test_transaction_3 = '0002020189475fa839c308f2c52f7c088037544709a7075e9de1e7f16e47077ed824d6450040d31c42f309a1e6742fe7efda401658f69221cb2ceec3fb8deb1ebe7db2117859a41ac4eb7a196cad3a3ddadacaccce4b9d967f7f60a839367a17628003a773970389475fa839c308f2c52f7c088037544709a7075e9de1e7f16e47077ed824d6450000030101005f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e3431382929408a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d6160201005f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e3431382929408a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d6160301005f504f4c59474f4e2028282d34372e383132352038362e3431382c202d34372e383132352038362e323339382c202d35302e3632352038362e323339382c202d35302e3632352038362e3431382c202d34372e383132352038362e3431382929408a482e4569ccb8cdbb910d6a64825888b3c790bccfdf2a19acfc2e969592d6fae046c47742aa4bcca55d433489baa29279d7fc2e11b9242235dadb6d62b9d61600174876e80032a001d1a94a200003e82a626331713435776e7364336132727a38346a6370323075363379343877346672646368616c3677737378'

    deserialized_test_landbase_1 = deserialize_transaction(unhexlify(test_landbase_1))
    deserialized_test_transaction_2 = deserialize_transaction(unhexlify(test_transaction_2))
    deserialized_test_transaction_3 = deserialize_transaction(unhexlify(test_transaction_3))
    
    print(deserialized_test_landbase_1)
    print(deserialized_test_transaction_2)
    print(deserialized_test_transaction_3)
    
    
    
    
        