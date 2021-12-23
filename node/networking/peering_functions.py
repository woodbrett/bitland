'''
Created on Jul 11, 2021

@author: brett_wood
'''
from utilities.sql_utils import *
from system_variables import (
    max_peer_count,
    peering_port,
    local_api_password
    )
from collections import namedtuple
import threading
import time
import requests
import json
from utilities.time_utils import getTimeNowSeconds

#external_contact_local_accepted
#local_contact_external_accepted

def evaluateInitialConnectionRequest(ip_address, version, port, timestamp):
        
    status = ''
    reason = ''
    token = ''
    
    current_peer_count = peerCount()
    #peer = queryPeer(ip_address=ip_address)
    peer = queryPeerByIpAndPort(ip_address, port)
    
    if current_peer_count >= max_peer_count:
        status = 'unsuccessful peer'
        reason = 'too many peers'

    #UPDATE to check for version
    
    #UPDATE to check for mainnet / testnet
    
    #UPDATE make logic smoother
    else:
        if peer.get('peer_status') != 'no peer found':
            deletePeer(ip_address, port)
            print('re-establishing connection with peer')
        else:
            print('new peer request')
            
        status = 'initial connection request accepted'
        reason = ''
        print(ip_address)
        print(port)
        token = str(addPeer(ip_address, port, 'external_contact_local_accepted'))
        #UPDATE version
        t1 = threading.Thread(target=responsivePeerRequest,args=(1, peering_port, getTimeNowSeconds(), ip_address, port,),daemon=True)
        t1.start()
    
    print("evaluated connection request: ")
    print(status)
    print(reason)
    
    return {
        "status": status,
        "reason": reason,
        "token": token
        }


def evaluateValidateConnectionRequest(ip_address, version, port, timestamp):
        
    status = ''
    reason = ''
    token = ''
    
    current_peer_count = peerCount()
    #peer = queryPeer(ip_address=ip_address)
    peer = queryPeerByIpAndPort(ip_address, port)
    
    if current_peer_count >= max_peer_count:
        status = 'unsuccessful peer'
        reason = 'too many peers'

    #UPDATE to check for version
    
    #UPDATE to check for mainnet / testnet
    
    #UPDATE make logic smoother
    elif peer.get('peer_status') != 'no peer found' and peer.get('status') == 'local_contact_external_accepted':
        status = 'successful peer'
        reason = ''
        updatePeer(ip_address=ip_address, port=port, status='connected')
        token = queryPeer(ip_address=ip_address).get('peer_auth_key')
            
    else:
        status = 'unsuccessful peer'
        
        if peer.get('peer_status') == 'no peer found':
            reason = 'no initial connection made'
        else:
            reason = 'not in validation status'
            deletePeer(ip_address, port)
        
        token = str(addPeer(ip_address, port, 'unpeered'))
                    
    print("evaluated connection request: ")
    print(status)
    print(reason)
    
    return {
        "status": status,
        "reason": reason,
        "token": token
        }
    

def authenticatePeer(ip_address, token):
    
    if queryPeer(ip_address=ip_address).get('peer_status') == 'no peer found':
        return False
    
    elif queryPeer(ip_address=ip_address).get('status') != 'connected':
        return False
    
    elif queryPeer(ip_address=ip_address).get('peer_auth_key') == token:
        return True
    
    else: 
        return False


def authenticateLocalUser(ip_address, password):
    
    if password == local_api_password and ip_address == '127.0.0.1':
        return True
    else:
        return False


def addPeer(ip_address,port,status,connected_time=0,last_ping=0):
    
    query = (
        "insert into networking.peer (ip_address, port, status, connected_time, last_ping) " +
        "values ('" + ip_address +"'," + str(port) + ",'" + status + "'," + str(connected_time) + "," + str(last_ping) + ") " +
        "returning peer_auth_key;"
        )
    
    print(query)
    
    try:
        add_peer = executeSql(query)[0]

    except Exception as error:
        add_peer = 'failure'    
    
    return add_peer


#UPDATE
def updatePeer(ip_address,port,status=0,connected_time=0,self_auth_key=0,peer_auth_key=0,derive_peer_auth_key=False,last_ping=0):
    
    x = ''
    
    print(port)
    
    if status != 0:
            x = x + "update networking.peer set status = '" + status + "' where ip_address = '" + ip_address + "' and port = " + str(port) + ";"
    if connected_time != 0:
        x = x + "update networking.peer set connected_time = " + str(connected_time) + " where ip_address = '" + ip_address + "' and port = " + str(port) + ";"
    if self_auth_key != 0:
        x = x + "update networking.peer set self_auth_key = '" + self_auth_key + "' where ip_address = '" + ip_address + "' and port = " + str(port) + ";"
    if peer_auth_key != 0:
        x = x + "update networking.peer set peer_auth_key = '" + peer_auth_key + "' where ip_address = '" + ip_address + "' and port = " + str(port) + ";"
    if derive_peer_auth_key == True:
        x = x + "update networking.peer set peer_auth_key = uuid_generate_v1() where ip_address = '" + ip_address + "' and port = " + str(port) + ";"
    if last_ping != 0:
        x = x + "update networking.peer set last_ping = " + str(last_ping) + " where ip_address = '" + ip_address + "' and port = " + str(port) + ";"
    
    try:
        update = executeSqlDeleteUpdate(x)
        
    except Exception as error:
        update = 'error with update'
    
    return update


def resetPeers():
    
    peers = queryPeers()
    
    for i in range(0,len(peers)):
        
        updatePeer(ip_address=peers[i].get('ip_address'),port=peers[i].get('port'),status='unpeered')
    
    return len(peers)


def queryPeer(ip_address = '', self_auth_key = '', peer_auth_key = ''):
    
    if ip_address == '' and self_auth_key == '' and peer_auth_key == '':

        query = (        
            "select ip_address ,port ,status ,connected_time ,last_ping ,self_auth_key ,peer_auth_key " +
            "from networking.peer " + ";")        
    
    else:
        query = (        
            "select ip_address ,port ,status ,connected_time ,last_ping ,self_auth_key ,peer_auth_key " +
            "from networking.peer " +
            "where ip_address = '" + ip_address + "' or self_auth_key::varchar = '" + self_auth_key + "' or peer_auth_key::varchar = '" + peer_auth_key + "';")
    
    try:
        peer_sql = executeSql(query)
        columns = namedtuple('columns', ['ip_address', 'port', 'status', 'connected_time', 'last_ping', 'self_auth_key', 'peer_auth_key'])
        peers = {
                    'peer_status': 'peer identified',
                    'ip_address': peer_sql[0],
                    'port': peer_sql[1],
                    'status': peer_sql[2],
                    'connected_time': peer_sql[3],
                    'last_ping': peer_sql[4],
                    'self_auth_key': peer_sql[5],
                    'peer_auth_key': peer_sql[6]
                }

    except Exception as error:
        peers = { 'peer_status': 'no peer found'}
    
    return peers 


def queryPeerByIpAndPort(ip_address, port):
    
    query = (        
        "select ip_address ,port ,status ,connected_time ,last_ping ,self_auth_key ,peer_auth_key " +
        "from networking.peer " +
        "where ip_address = '" + ip_address + "' and port = " + str(port) + ";")
    
    try:
        peer_sql = executeSql(query)
        columns = namedtuple('columns', ['ip_address', 'port', 'status', 'connected_time', 'last_ping', 'self_auth_key', 'peer_auth_key'])
        peers = {
                    'peer_status': 'peer identified',
                    'ip_address': peer_sql[0],
                    'port': peer_sql[1],
                    'status': peer_sql[2],
                    'connected_time': peer_sql[3],
                    'last_ping': peer_sql[4],
                    'self_auth_key': peer_sql[5],
                    'peer_auth_key': peer_sql[6]
                }

    except Exception as error:
        peers = { 'peer_status': 'no peer found'}
    
    return peers 


def queryPeers(ip_address = '', self_auth_key = '', peer_auth_key = ''):
    
    if ip_address == '' and self_auth_key == '' and peer_auth_key == '':

        query = (        
            "select ip_address ,port ,status ,connected_time ,last_ping ,self_auth_key ,peer_auth_key " +
            "from networking.peer " + ";")        
    
    else:
        query = (        
            "select ip_address ,port ,status ,connected_time ,last_ping ,self_auth_key ,peer_auth_key " +
            "from networking.peer " +
            "where ip_address = '" + ip_address + "' or self_auth_key::varchar = '" + self_auth_key + "' or peer_auth_key::varchar = '" + peer_auth_key + "';")
    
    peer_sql = executeSqlMultipleRows(query)
    
    dict_array = []
    for i in range(0,len(peer_sql)):
        dicti = {
            'ip_address': peer_sql[i][0],
            'port': peer_sql[i][1],
            'status': peer_sql[i][2],
            'cpmmected_time': peer_sql[i][3],
            'last_ping': peer_sql[i][4],
            'self_auth_key': peer_sql[i][5],
            'peer_auth_key': peer_sql[i][6]
            }
        dict_array.append(dicti)
    
    return dict_array


def askPeersForHeight():
    
    heights = messageAllKnownPeers('/peer/node_queries/getBlockHeight', rest_type='get')
    
    return heights


#UPDATE
def askPeerForBlocks(peer, start_block, end_block):

    url = '/peer/node_queries/getBlocks/' + str(start_block) + '/' + str(end_block)
    
    blocks = messagePeer(url, peer, rest_type='get')
    
    print(blocks)
    
    return blocks


def peerCount():
    
    query = ("select count(*) from networking.peer where status = 'connected'")

    try:
        peer_count = executeSql(query)[0]

    except Exception as error:
        peer_count = 'no peer found'
    
    return peer_count


def deletePeer(ip_address, port):
    
    query = ("delete from networking.peer where ip_address = '" + ip_address + "' and port = " + str(port) + ";")
        
    try:
        delete = executeSqlDeleteUpdate(query)

    except Exception as error:
        print('error deleting' + str(error))
        delete = 'error deleting'
    
    return delete


def initialConnectToPeer(version, port, timestamp, peer_ip_address, peer_port):
    
    #curl -X POST "http://localhost:8334/peer/peering/connect" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"version\": \"abc\", \"port\": 100, \"timestamp\": 100}"
    
    url = "http://" + peer_ip_address + ":" + str(peer_port) + "/peer/peering/initial_connect" 
    print(url)
    payload = {'version':version,'port':port,'timestamp':timestamp}
    print(payload)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    r = requests.post(url, data=json.dumps(payload), headers=headers).json()
    
    return {
        'status': r.get('status'),
        'reason': r.get('reason'),
        'token': r.get('token')
    }
    

def validateConnectToPeer(version, port, timestamp, peer_ip_address, peer_port):
    
    #curl -X POST "http://localhost:8334/peer/peering/connect" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"version\": \"abc\", \"port\": 100, \"timestamp\": 100}"
    
    url = "http://" + peer_ip_address + ":" + str(peer_port) + "/peer/peering/validate_connect" 
    print(url)
    payload = {'version':version,'port':port,'timestamp':timestamp}
    print(payload)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    r = requests.post(url, data=json.dumps(payload), headers=headers).json()
    
    return {
        'status': r.get('status'),
        'reason': r.get('reason'),
        'token': r.get('token')
    }
    

def responsivePeerRequest(version, port, timestamp, peer_ip_address, peer_port, wait_time=5):
    
    time.sleep(wait_time)
    
    peer_request = validateConnectToPeer(version, port, timestamp, peer_ip_address, peer_port)
    
    if peer_request.get('status') == 'successful peer':
        updatePeer(ip_address=peer_ip_address, port=port, self_auth_key=peer_request.get('token'), status='connected')
        return 'Success'
    
    else:
        return 'Fail'    
    

def attemptToConnectToNewPeer(version, port, timestamp, peer_ip_address, peer_port):
    
    peer_request = initialConnectToPeer(version, port, timestamp, peer_ip_address, peer_port)
    
    if peer_request.get('status') == 'initial connection request accepted':
        addPeer(peer_ip_address,peer_port,'local_contact_external_accepted')
        updatePeer(ip_address=peer_ip_address, port=port, self_auth_key=peer_request.get('token'))
        return 'Success'
    
    else:
        return 'Fail'
    
    
#UPDATE 
#add threading
#currently hardcoded to the structure of the peers query
#very inelegant with the post/get/etc rest type
#hardcoded auth
def messageAllKnownPeers(endpoint, payload='', rest_type='get', peers_to_exclude=[], peer_types=['connected']):

    peers = queryPeers()
    
    responses = []
    
    for i in range(0 ,len(peers)):
        exclude_peer = False
        peer_ip_address = peers[i].get('ip_address')
        peer_port = peers[i].get('port')
        peer_status = peers[i].get('status')
        token = peers[i].get('self_auth_key')

        for j in range(0,len(peers_to_exclude)):
            if peer_ip_address == peers_to_exclude[j]:
                exclude_peer = True
        
        if exclude_peer == False and peer_status in peer_types:
            url = "http://" + peer_ip_address + ":" + str(peer_port) + endpoint
            headers = {
                'Content-type': 'application/json', 
                'Accept': 'application/json', 
                'Authorization': token 
            }
            
            if rest_type == 'get':
                try:
                    r = requests.get(url, headers=headers).json()
                except Exception as error:
                    print('error calling peer ' + peer_ip_address)
                    r = 'error calling peer'
            
            if rest_type == 'post':
                try:
                    r = requests.post(url, data=json.dumps(payload), headers=headers).json()
                except Exception as error:
                    print('error calling peer ' + peer_ip_address)
                    r = 'error calling peer'
            
            if rest_type == 'put':
                try:
                    r = requests.put(url, data=json.dumps(payload), headers=headers).json()
                except Exception as error:
                    print('error calling peer ' + peer_ip_address)
                    r = 'error calling peer'
            
            updatePeer(ip_address=peer_ip_address, port=peer_port, last_ping=getTimeNowSeconds())
            
            responses.append(
                {'peer_ip_address':peer_ip_address,
                 'peer_ip_address':peer_port,
                 'response':r})

    return responses


#UPDATE 
#currently hardcoded to the structure of the peers query
#very inelegant with the post/get/etc rest type
#hardcoded auth
def messagePeer(endpoint, peer_ip_address, payload='', rest_type='get'):

    peer = queryPeer(peer_ip_address)

    url = "http://" + peer_ip_address + ":" + str(peer.get('port')) + endpoint
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'application/json', 
        'Authorization': peer.get('self_auth_key')
    }

    if rest_type == 'get':
        try:
            r = requests.get(url, headers=headers).json()
        except Exception as error:
            print('error calling peer ' + peer_ip_address)
            r = 'error calling peer'
    
    if rest_type == 'post':
        try:
            r = requests.post(url, data=json.dumps(payload), headers=headers).json()
        except Exception as error:
            print('error calling peer ' + peer_ip_address)
            r = 'error calling peer'
            
    if rest_type == 'put':
        try:
            r = requests.put(url, data=json.dumps(payload), headers=headers).json()
        except Exception as error:
            print('error calling peer ' + peer_ip_address)
            r = 'error calling peer'
    
    return r

    
if __name__ == '__main__':
    
    #attemptToConnectToNewPeer(1, 8334, getTimeNowSeconds(), '76.179.199.85', 8336)
    
    evaluateConnectionRequest('74.78.100.60', 1, 8336, 1)
    print(queryPeerByIpAndPort('124.123.66.141',8334))
    
    
    