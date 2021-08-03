'''
Created on Nov 13, 2020

@author: brett_wood
'''


import ecdsa
import hashlib
from binascii import unhexlify, hexlify
from codecs import encode, decode
import base58



'''
private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) 
private_key_pretty = hexlify(private_key.to_string()).decode("utf-8")
print(private_key_pretty)
'''

private_key_pretty = "17bccd419598fd3f1107cffc88c31b0121561fa5add55c8bf79b601c728ba886"
private_key = ecdsa.SigningKey.from_string(unhexlify(private_key_pretty.encode("utf-8")),curve=ecdsa.SECP256k1)

message = b'\01'

verifying_key = private_key.verifying_key

#print(verifying_key)

verifying_key_pretty = hexlify(verifying_key.to_string()).decode("utf-8")

print(verifying_key_pretty)

signature = private_key.sign(message)

#print(signature)

signature_pretty = hexlify(signature).decode("utf-8")

print(signature_pretty)

print(verifying_key.verify(signature, message))


shape_text = b"POLYGON ((-71.75 44.25, -71.75 44.5, -71.5 44.5, -71.5 44.25, -71.75 44.25))"

shape_pretty = hexlify(shape_text).decode("utf-8")

print(shape_pretty)

shape_base58 = base58.b58encode(shape_text)

print(shape_base58)



