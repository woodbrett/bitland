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
global mining_path
global local_api_username 
global local_api_password 
global peer_list 
global transaction_validation_url
global rpc_user
global rpc_password 
global node_url
global run_node_var
global run_mining_var
global initial_synch_var
global min_peer_count
global internet_connectivity_test_source

#bitcoin information
block_height_url = 'https://blockstream.info/api/blocks/tip/height'
address_search_url = 'https://blockstream.info/api/address/:address/txs'
transaction_validation_url = 'https://blockstream.info/api/address/:address'
get_block_by_hash_url = 'https://blockstream.info/api/block/:hash/raw'
get_block_hash_by_height_url = 'https://blockstream.info/api/block-height/:height'
block_hash_tip_url = 'https://blockstream.info/api/blocks/tip/hash'
last_ten_block_hashes_url = 'https://blockstream.info/api/blocks/:height'
get_block_height_by_hash_url = 'https://blockstream.info/api/block/:hash'

#other
min_peer_count = 1
max_peer_count = 5
peering_port = 8336
peering_host = "0.0.0.0"
mainnet_database_settings_file_location = 'C:/other/database.ini'
testnet_database_settings_file_location = 'C:/other/testnet_database.ini'
mining_path = 'MULTILINESTRING ((-24.32582123586823 89.84080925775434, -74.62860694880915 82.52182923327297, -91.10241210722151 75.38399911209015, -95.0423241796008 66.86026257852093, -100.6851598368639 54.57263922226819),(-101.3573454825694 55.02763381008007, -82.54937943634791 31.48094731046708),(-99.09477782473776 54.17424604757469, -110.205550984981 30.49451859774517, -96.77412063206563 28.15864596136793))'
local_api_username = 'admin'
local_api_password = 'password'
peer_list = []

#local bitcoin node information rpc_user and rpc_password are set in the bitcoin.conf file
rpc_user = 'admin'
rpc_password = 'password'
node_url = '192.168.86.34:8332'

#running node
run_node_var = True
run_mining_var = True
initial_synch_var = False
bitcoin_source = 'local_node' #local_node or blockstream_api
node_network = 'mainnet' #mainnet or testnet
internet_connectivity_test_source = 'http://www.blockstream.com'

#wallet
override_ip_to_allow_remote_wallet_access = False