'''
Created on Mar 26, 2021

@author: brett_wood
'''
from binascii import unhexlify,hexlify

def serializeMessage(network, command, message_body):
    
    message_body_len = len(message_body)
    message_body_len = message_body_len.to_bytes(4, byteorder = 'big')
    
    serialized_message = network + command + message_body_len + message_body
    
    return serialized_message


def deserializeMessage(message):

    counter = 0    
    network_bytes = 8
    command_bytes = 2
    message_body_len_bytes = 4

    network = message[counter:(counter + network_bytes)]
    counter = counter + network_bytes

    command = message[counter:(counter + command_bytes)]
    counter = counter + command_bytes

    body_len = message[counter:(counter + message_body_len_bytes)]
    body_len_int = int.from_bytes(body_len, byteorder='big')
    counter = counter + message_body_len_bytes

    body = message[counter:(counter + body_len_int)]
    counter = counter + body_len_int
    
    return network, command, body


def deserializeBody(command, body):
    
    if command == 'getHeaders':
        start_hash = body[0:32]
        end_hash = body[32:64]
        return (start_hash, end_hash)


if __name__ == '__main__':

    network = b'f9beb4d9' #mainnet
    command = 1
    command = command.to_bytes(4, byteorder = 'big')
    
    hash = '000100000000000000000000000000000000000000000000000000000000000000002b7334323d293f909f3d3458ff6641a5c299838f229d6ae9d0d18b2cf4f56af4006061242d1d00ffff000a604033313335346537373535366237343561373433343662353734643463373134623335353134633732373834313464353136313730373936353436373834313639333636381f1471ce'
    hash = unhexlify(hash.encode('utf-8'))
    print(hash)
    print(len(hash))
    
    #message_text = ''
    #message = hexlify(message_text.encode('utf-8'))
    message = hash + hash
    
    print(message)
    print(command)
    
    serialized_message = serializeMessage(network, command, message)
    print(serialized_message)
    print(hexlify(serialized_message))
    deserialized_message = deserializeMessage(serialized_message)
    print(deserialized_message)
    
