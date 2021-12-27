global block_height_url 
global address_search_url
global max_peer_count
global peering_port
global peering_host
global mainnet_database_settings_file_location
global testnet_database_settings_file_location
global local_api_username
global local_api_password
global peer_list
global transaction_validation_url
global rpc_user
global rpc_password 
global node_url
global get_block_by_hash_url
global bitcoin_source
global get_block_hash_by_height_url
global block_hash_tip_url
global last_ten_block_hashes_url
global get_block_height_by_hash_url
global node_network

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
peering_port = 8334
peering_host = "0.0.0.0"
mainnet_database_settings_file_location = '/home/prakasha/source/bitland/database.ini'
testnet_database_settings_file_location = '/home/prakasha/source/bitland/testnet_database.ini'
mining_path = 'MULTILINESTRING ((-24.32582123586823 89.84080925775434, -74.62860694880915 82.52182923327297, -91.10241210722151 75.38399911209015, -95.0423241796008 66.86026257852093, -100.6851598368639 54.57263922226819),(-101.3573454825694 55.02763381008007, -82.54937943634791 31.48094731046708),(-99.09477782473776 54.17424604757469, -110.205550984981 30.49451859774517, -96.77412063206563 28.15864596136793))'
local_api_username = 'admin'
local_api_password = 'password'
peer_list = []

#local bitcoin node information rpc_user and rpc_password are set in the bitcoin.conf file
rpc_user = 'admin'
rpc_password = 'password'
node_url = '192.168.86.34:8332'

#running node
run_node_var = False
run_mining_var = False
initial_synch_var = True
bitcoin_source = 'blockstream_api' #local_node or blockstream_api
node_network = 'mainnet' #mainnet or testnet