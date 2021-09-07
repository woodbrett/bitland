'''
Created on Feb 14, 2021

@author: brett_wood
'''


import struct
from codecs import decode, encode
from binascii import hexlify, unhexlify

def serialize_text(text):
    
    text_encode = str.encode(text)
    text_hex = encode(text_encode, "hex")
    text_utf8 = text_hex.decode('utf-8')
    return text_utf8


def deserialize_text(text_hex):
    
    text_utf8 = text_hex
    text_hex = text_utf8.encode('utf-8')
    text_encode = decode(text_hex, "hex")
    text = text_encode.decode('utf-8')
    return text
