'''
Created on Feb 22, 2021

@author: brett_wood
'''
import ecdsa
import hashlib
from binascii import unhexlify, hexlify
from codecs import encode, decode
from utilities.sqlUtils import executeSql
from blockchain.transaction_serialization import serialize_transaction, deserialize_transaction

#INPUTS
lat = 89.855533
long = -57.348142
version = 1
output_1_planet = 1


#POLYGON
query_landbase_polygon = 'select st_astext(geom) from landbase_enum le where st_intersects(geom,st_setsrid(st_makePoint(' + str(long) + ',' + str(lat) + '),4326)) and valid_claim = true'
#print(query_landbase_polygon)

try:
    landbase_polygon = executeSql(query_landbase_polygon)[0]

except Exception as error:
    print('landbase not available')

print(landbase_polygon)

#KEYS
private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) 
private_key_hex = hexlify(private_key.to_string()).decode("utf-8")
print(private_key_hex)

#private_key = ecdsa.SigningKey.from_string(unhexlify(private_key_pretty.encode("utf-8")),curve=ecdsa.SECP256k1)

message = landbase_polygon.encode('utf-8')
print(message)

verifying_key = private_key.verifying_key
verifying_key_hex = hexlify(verifying_key.to_string()).decode("utf-8")

print(verifying_key_hex)

signature = private_key.sign(message)

print(signature)
print(verifying_key.verify(signature, message))


#SAVE private and public key to DB
query_insert_keys = "insert into wallet.addresses (private_key, public_key) values ('" + private_key_hex + "','" + verifying_key_hex + "') RETURNING public_key;"
print(query_insert_keys)

try:
    insert = executeSql(query_insert_keys)[0]

except Exception as error:
    print('error inserting keys' + str(error))
    
    
#CREATE TRANSACTION
inputs = []
output_1_shape = landbase_polygon
output_1_script = verifying_key_hex
contingencies = []
claims = []

version_bytes = version.to_bytes(2, byteorder = 'big')
inputs_bytes = inputs

output_1_planet_bytes = output_1_planet.to_bytes(1, byteorder = 'big')
output_1_shape_bytes = output_1_shape.encode('utf-8')
output_1_script_bytes = unhexlify(verifying_key_hex)
output_1_bytes = [output_1_planet_bytes,output_1_shape_bytes,output_1_script_bytes]
outputs_bytes = [output_1_bytes]

contingencies_bytes = contingencies
claims_bytes = claims

serialized_transaction_1 = serialize_transaction(
    version_bytes, #version
    inputs_bytes, #inputs
    outputs_bytes, #outputs
    contingencies_bytes, #contingencies
    claims_bytes #claims
    )

print(serialized_transaction_1)
print("transaction: " + str(hexlify(serialized_transaction_1).decode('utf-8')))

print(deserialize_transaction(serialized_transaction_1))









