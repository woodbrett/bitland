'''
Created on Mar 16, 2021

@author: brett_wood
'''
import socket
import time
import random
import struct
import hashlib
import binascii
import sys
import threading
import concurrent.futures.thread
from concurrent.futures.thread import ThreadPoolExecutor
from binascii import hexlify, unhexlify
from future.backports.urllib.parse import to_bytes
from network_serialization import *
from commands import commands, dataTypes
from blockchain.header_operations import getHeaders
#https://pymotw.com/2/socket/tcp.html

peers = []

class Peer:
    def __init__(self, ip_address, port, version_verified, version_sent, verack_received, verack_sent, is_peer):
        self.ip_address = ip_address 
        self.port = port
        self.version_verified = version_verified
        self.version_sent = version_sent
        self.verack_received = verack_received
        self.verack_sent = verack_sent
        self.is_peer = is_peer


def testBroadcast():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    server_name = 'localhost' #socket.gethostbyname(socket.gethostname())
    print(server_name)
    server_address = (server_name, 8334)

    print (sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    
    try:
        
        # Send data
        message = 'This is the message.  It will be repeated.'
        message = message.encode('utf-8')
        print (sys.stderr, 'sending "%s"' % message)
        sock.sendall(message)
    
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print (sys.stderr, 'received "%s"' % data)
    
    finally:
        print (sys.stderr, 'closing socket')
        sock.close()

             
def sendToPeer(server_name, server_port, message):
    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    server_address = (server_name, server_port)

    print (sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    
    #sock = socket.create_connection(address=('localhost',8334),source_address=('',10000))
    
    try:
        
        # Send data
        print (sys.stderr, 'sending "%s"' % message)
        sock.sendall(message)
    
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        
        while amount_received < amount_expected:
            data = sock.recv(1000)
            amount_received += len(data)
            print (sys.stderr, 'received "%s"' % data)
    
    finally:
        print (sys.stderr, 'closing socket')
        sock.close()


def listenForPeers(server_name, server_port):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the port
    server_address = (server_name, server_port)
        
    print(sys.stderr, 'starting up on %s port %s' % server_address)
    sock.bind(server_address)
    
    # Listen for incoming connections
    sock.listen(5)
    
    global peers
    
    while True:
        # Wait for a connection
        print(sys.stderr, 'waiting for a connection')
        connection, client_address = sock.accept()
        
        #is_peer = client_address[0] in peers
        message = readMessageFromPeer(connection, client_address)
        
        processMessage(message, client_address)

        
def readMessageFromPeer(connection, client_address):

    print("reading message from peer")
    aggregated_data = bytearray()  
    
    try:
        print(sys.stderr, 'connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1000)
            print(sys.stderr, 'received "%s"' % data)
            if data:
                print(sys.stderr, 'sending data back to the client')
                connection.sendall(data)
                aggregated_data = aggregated_data + data
            else:
                print(sys.stderr, 'no more data from', client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()
    
    return aggregated_data


#UPDATE
def processMessage(message, client_address):
    
    peer_status = getPeerInfo(client_address)
    if peer_status == False:
        new_peer = Peer(client_address,False,False,False,False,False)
        peer_status = new_peer
    
    print(peer_status)
    
    if peer_status.is_peer == False:
        #UPDATE to send message if not accepting new peers

        deserialized_message = deserializeMessage(message)
        command = deserialized_message[1]
        body = deserialized_message[2]
        
        if peer_status.version_verified == False and command == 'version':
            valid_version = validatePeerVersion()
            peer_status.version_verified = valid_version
        
        if peer_status.verack_received == False and command == 'verack':
            valid_verack = validatePeerVerack(body)
            peer_status.verack_received = valid_verack
            
        if peer_status.version_verified == True and peer_status.version_sent == False:
            sendVersion()
            
        if peer_status.version_verified == True and peer_status.verack_sent == False:
            sendVerack()
            
        peer_status.is_peer = analyzeIsPeer(peer_status)
                    
    if peer_status.is_peer == True:
        analyzeMessage(message, peer_status)
    
    return True


def getPeerInfo(client_address):
    global peers
    for i in range(0, len(peers)):
        peer = peers[i]
        if peer.ip_address == client_address:
            return peer
            break
    
    return False
    

#UPDATE
def analyzeMessage(message, peer):
   
    deserialized_message = deserializeMessage(message)
    command = int.from_bytes(deserialized_message[1], byteorder='big')
    command_text = commands(command_number = command)[0]
    body = deserialized_message[2]
    
    if command_text == 'getHeaders':
        deserialized_body = deserializeBody(command_text, body)
        start_header = deserialized_body[0]
        end_header = deserialized_body[1]
        response_command = commands(command_text = 'data')[1].to_bytes(2, byteorder = 'big')
        headers = getHeaders(start_header,end_header)
        
        response_body = b''
        for i in range(0, len(headers)):
            header = headers[i]
            header_len = len(header).to_bytes(4, byteorder = 'big')
            data_type = dataTypes(data_type_text = 'header')[1].to_bytes(2, byteorder = 'big')
            response_body = response_body + data_type + header_len + header
        
        response_message = serializeMessage(b'f9beb4d9', response_command, response_body)
        print(response_message)
        print(hexlify(response_message))
        print(response_message.decode('utf-8'))
        
        sendToPeer(peer.ip_address, peer.port, response_message)
    
    #if command_text = 'data':
        
        
    
    return True


#UPDATE
def sendBlocksToPeer():
    return True


#UPDATE
def validatePeerVersion():
    return True


#UPDATE
def validatePeerVerack():
    return True


#UPDATE
def sendVersion():
    return True


#UPDATE
def sendVerack():
    return True


#UPDATE
def analyzeIsPeer(peer):
    is_peer = peer.version_verified and peer.version_sent and peer.verack_received and peer.verack_sent
    return is_peer



if __name__ == '__main__':
    
    #listenForPeers('localhost',8334)
    #peering('localhost',8334)
    
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #socket.create_connection(address=('localhost',8334),source_address=('',1000))

    print(socket.gethostbyname(socket.gethostname()))
    print(socket.gethostname())
    socket_connection = 'localhost' #socket.gethostname() #'76.179.199.85' #'localhost'

    #x=Peer('76.179.199.85',True,True,True,True,True)
    x=Peer('192.168.0.29',8334,True,True,True,True,True)
    peers.append(x)

    threading.Thread(target=listenForPeers,args=('0.0.0.0',8334)).start()
    
    #test sending headers
    hash1 = '0000000000000000000000000000000000000000000000000000000000000000'
    hash1  = unhexlify(hash1.encode('utf-8'))
    hash2 = '0000000000000000000000000000000000000000000000000000000000000000'
    hash2  = unhexlify(hash2.encode('utf-8'))
    body = hash1 + hash2
    command = commands(command_text = 'getHeaders')[1].to_bytes(2, byteorder = 'big')
    message = serializeMessage(b'f9beb4d9', command, body)
    print(analyzeMessage(message, peers[0]))
    
    #test receiving headers
    
    
    '''
    time.sleep(5)
    print("a")
    
    version = 1
    message1 = '1'
    message1 = message1.encode('utf-8')
    sendToPeer(x.ip_address,8336,message1)
    #threading.Thread(target=sendToPeer, args=('localhost',8334,message1)).start()
    
    time.sleep(5)
    print("b")
    
    message2 = 'hello, glad to be your peer'
    message2 = message2.encode('utf-8')
    sendToPeer(x.ip_address,8334,message2)
    '''