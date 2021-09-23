'''
Created on Sep 23, 2021

@author: admin
'''
from utilities.sql_utils import executeSqlMultipleRows

def getWalletUtxos():
    
    select = ("select private_key, public_key , transaction_hash, vout,output_version, st_astext(geom) as shape, planet_id, block_id as block_height, miner_fee_status, transfer_fee_status, claim_on_parcel from wallet.addresses a join bitland.utxo u on a.public_key = u.pub_key;")
    utxos = []
    
    try:
        db_utxos = executeSqlMultipleRows(select)
        
        for i in range(0, len(db_utxos)):
            db_utxos_i = db_utxos[i]
            utxo = {
                'private_key': db_utxos_i[0], 
                'public_key': db_utxos_i[1], 
                'transaction_hash': db_utxos_i[2], 
                'vout': db_utxos_i[3], 
                'output_version': db_utxos_i[4], 
                'shape': db_utxos_i[5], 
                'planet_id': db_utxos_i[6], 
                'block_height': db_utxos_i[7], 
                'miner_fee_status': db_utxos_i[8], 
                'transfer_fee_status': db_utxos_i[9],
                'claim_on_parcel': db_utxos_i[10]
            }
            utxos.append(utxo)
    
        output = {
            'status': 'utxos identified',
            'utxos': utxos
            }
        
    except Exception as error:
        output = {
            'status': 'no utxos',
        }    

    return output 


if __name__ == '__main__':
    
    getWalletUtxos()
