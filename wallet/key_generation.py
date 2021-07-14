'''
Created on Feb 24, 2021

@author: brett_wood
'''
import ecdsa
import hashlib
from binascii import unhexlify, hexlify
from codecs import encode, decode
from utilities.sqlUtils import executeSql

#KEYS
def generateRandomKeys():
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) 
    private_key_hex = hexlify(private_key.to_string()).decode("utf-8")
    public_key = private_key.verifying_key
    public_key_hex = hexlify(public_key.to_string()).decode("utf-8")
    
    return(private_key_hex, public_key_hex)


#SAVE private and public key to DB
def savePublicPrivateKeysDb(private_key_hex, public_key_hex):
    query_insert_keys = "insert into wallet.addresses (private_key, public_key) values ('" + private_key_hex + "','" + public_key_hex + "') RETURNING public_key;"
    print(query_insert_keys)
    
    try:
        insert = executeSql(query_insert_keys)[0]
    
    except Exception as error:
        print('error inserting keys' + str(error))