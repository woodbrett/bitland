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
from ipaddress import ip_address
from _datetime import datetime

#external_contact_local_accepted
#local_contact_external_accepted

def evaluateConnectionRequest(ip_address, version, port, timestamp):
        
    status = ''
    reason = ''
    token = ''
    
    current_peer_count = peerCount()
    peer = queryPeer(ip_address=ip_address)
    
    if current_peer_count >= max_peer_count:
        status = 'unsuccessful peer'
        reason = 'too many peers'

    #UPDATE to check for version
    
    #UPDATE make logic smoother
    elif peer.get('peer_status') != 'no peer found':
        if peer.get('status') == 'local_contact_external_accepted':
            status = 'successful peer'
            reason = ''
            updatePeer(ip_address=ip_address, port=port, status='connected')
            token = queryPeer(ip_address=ip_address).get('peer_auth_key')
        else:
            status = 'unsuccessful peer'
            reason = 'already exist as peer'
                
    else:
        status = 'successful peer'
        reason = ''
        token = str(addPeer(ip_address, port, 'external_contact_local_accepted'))
        #UPDATE version
        t1 = threading.Thread(target=responsivePeerRequest,args=(1, peering_port, int(time.time()), ip_address, port,),daemon=True)
        t1.start()
    
    vars = namedtuple('vars', ['status','reason','token'])
    
    print("evaluated connection request: ")
    print(status)
    print(reason)
    
    return vars(
        status,
        reason,
        token
    )
    

def authenticatePeer(ip_address, token):
    
    if queryPeer(ip_address=ip_address).get('peer_status') == 'no peer found':
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


def addPeer(ip_address,port,status):
    
    query = (
        "insert into networking.peer (ip_address, port, status) " +
        "values ('" + ip_address +"'," + str(port) + ",'" + status + "') " +
        "returning peer_auth_key;"
        )
    
    try:
        add_peer = executeSql(query)[0]

    except Exception as error:
        add_peer = 'failure'    
    
    return add_peer


#UPDATE
def updatePeer(ip_address,port="null",status="null",connected_time="null",self_auth_key="null",peer_auth_key="null",derive_peer_auth_key=False,last_ping="null"):
    
    x = ''
    
    if port != "null":
        x = x + ",port = " + str(port) + " "
    if status != "null":
        x = x + ",status = '" + status + "' "
    if connected_time != "null":
        x = x + ",connected_time = '" + connected_time + "' "
    if self_auth_key != "null":
        x = x + ",self_auth_key = '" + self_auth_key + "' "
    if peer_auth_key != "null":
        x = x + ",peer_auth_key = '" + peer_auth_key + "' "
    if derive_peer_auth_key == True:
        x = x + ",peer_auth_key = " + peer_auth_key + "uuid_generate_v1() "
    if last_ping != "null":
        x = x + ",last_ping = now() "
    
    query = (
        "update networking.peer " +
        "set " +
        "  ip_address = '" + ip_address + "'" +
        x + 
        " where ip_address = '" + ip_address + "';"
        )
    
    try:
        update = executeSqlDeleteUpdate(query)
        
    except Exception as error:
        update = 'error with update'
    
    return update


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
        peers = { 'peer_status': 'peer identified'}
    
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
        

def peerCount():
    
    query = ('select count(*) from networking.peer')

    try:
        peer_count = executeSql(query)[0]

    except Exception as error:
        peer_count = 'no peer found'
    
    return peer_count


def deletePeer(ip_address):
    
    query = ("delete from networking.peer where ip_address = '" + ip_address +"';")
        
    try:
        delete = executeSqlDeleteUpdate(query)

    except Exception as error:
        print('error deleting' + str(error))
        delete = 'error deleting'
    
    return delete


def connectToPeer(version, port, timestamp, peer_ip_address, peer_port):
    
    #curl -X POST "http://localhost:8334/peer/peering/connect" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"version\": \"abc\", \"port\": 100, \"timestamp\": 100}"
    
    url = "http://" + peer_ip_address + ":" + str(peer_port) + "/peer/peering/connect" 
    print(url)
    payload = {'version':version,'port':port,'timestamp':timestamp}
    print(payload)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    r = requests.post(url, data=json.dumps(payload), headers=headers).json()
    
    vars = namedtuple('vars', ['status','reason','token'])
    return vars(
        r.get('status'),
        r.get('reason'),
        r.get('token')
    )
    

def responsivePeerRequest(version, port, timestamp, peer_ip_address, peer_port, wait_time=30):
    
    time.sleep(wait_time)
    
    peer_request = connectToPeer(version, port, timestamp, peer_ip_address, peer_port)
    
    if peer_request.status == 'successful peer':
        updatePeer(ip_address=peer_ip_address, self_auth_key=peer_request.token, status='connected')
        return 'Success'
    
    else:
        return 'Fail'    
    

def attemptToConnectToNewPeer(version, port, timestamp, peer_ip_address, peer_port):
    
    peer_request = connectToPeer(version, port, timestamp, peer_ip_address, peer_port)
    
    if peer_request.status == 'successful peer':
        addPeer(peer_ip_address,peer_port,'local_contact_external_accepted')
        updatePeer(ip_address=peer_ip_address, self_auth_key=peer_request.token)
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
    
    print(peers)
    print(peer_types)
    
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
            
            updatePeer(ip_address=peer_ip_address, last_ping="x")
            
            responses.append(
                {'peer_ip_address':peer_ip_address,
                 'response':r.get('message')})

    return responses


#UPDATE 
#currently hardcoded to the structure of the peers query
#very inelegant with the post/get/etc rest type
#hardcoded auth
def messagePeer(endpoint, peer_ip_address, payload='', rest_type='get'):

    peer = queryPeer(peer_ip_address)

    url = "http://" + peer_ip_address + ":" + str(peer.port) + endpoint
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'application/json', 
        'Authorization': peer.get('self_auth_key ')
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
    
    payload = {"transaction":"0002010103aca220f7ec55e458acd9aafadc9af571da0676846fb6d5e2505c82a8849782004078708125ab06305a739e7ac4dbc7f0a3a571aad4976369069cf27469262b6f8650d0b508b73e36953f3b59934abc2ddad4ef5442114bae127d9efc49ba8810080101010051504f4c59474f4e28282d32322e352038392e37343637342c2d32322e352038392e35313836382c2d34352038392e35313836382c2d34352038392e37343637342c2d32322e352038392e373436373429294069022ccf1a0644a5e07eb2f89b3e9ab217fcc158f3525655a2a30f66c0c61a916858846f55db7172d5e71e3399d18fc191f0efc9b1fa12efcaeab17e0bbe27db0000000000000000000000000000000000"}
    url = "/peer/node_updates/sendNewTransaction"
    rest_type = 'put'
    
    peers_to_exclude=[]
    
    messagePeer(url, '76.179.199.85', payload=payload, rest_type=rest_type)
    
    
    
    