'''
Created on Feb 15, 2021

@author: brett_wood
'''

global block_height_url 
global address_search_url
global max_peer_count
global peering_port
global peering_host
global database_settings_file_location

block_height_url = 'https://blockstream.info/api/blocks/tip/height'
address_search_url = 'https://blockstream.info/api/address/:address/txs'
max_peer_count = 5
peering_port = 8336
peering_host = "0.0.0.0"
database_settings_file_location = 'C:/other/database.ini'

