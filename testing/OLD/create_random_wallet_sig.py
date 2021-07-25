'''
Created on Nov 13, 2020

@author: brett_wood
'''

import ecdsa
import hashlib
from binascii import unhexlify, hexlify
from codecs import encode, decode
import base58

#shape_hex = b"POLYGON ((-71.75 44.25, -71.75 44.5, -71.5 44.5, -71.5 44.25, -71.75 44.25))"
shape_hex = b"POLYGON ((-71.5 44.25, -71.5 44.5, -71.25 44.5, -71.25 44.25, -71.5 44.25))"
shape_base58 = base58.b58encode(shape_hex)
print("transaction: " + shape_base58.decode("utf-8"))

private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) 
private_key_pretty = hexlify(private_key.to_string()).decode("utf-8")
private_key_hex = private_key.to_string()
private_key_base58 = base58.b58encode(private_key_hex)
print("private key: " + private_key_base58.decode("utf-8"))

verifying_key = private_key.verifying_key
verifying_key_pretty = hexlify(verifying_key.to_string()).decode("utf-8")
verifying_key_hex = verifying_key.to_string()
verifying_key_base58 = base58.b58encode(verifying_key_hex)
print("verifying key: " + verifying_key_base58.decode("utf-8"))

signature = private_key.sign(shape_hex)
signature_pretty = hexlify(signature).decode("utf-8")
signature_base58 = base58.b58encode(signature)
print("signature: " + signature_base58.decode("utf-8"))



print(verifying_key)
print(signature)
print(shape_hex)
print(verifying_key.verify(signature, shape_hex))





