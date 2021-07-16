'''
Created on Jul 11, 2021

@author: brett_wood
'''
from utilities.sqlUtils import *
from system_variables import (
    max_peer_count,
    peering_port
    )
from collections import namedtuple
import threading
import time
import requests
import json
from ipaddress import ip_address

#external_contact_local_accepted
#local_contact_external_accepted

def evaluate_connection_request(ip_address, version, port, timestamp):
        
    status = ''
    reason = ''
    token = ''
    
    current_peer_count = peer_count()
    peer = query_peer(ip_address=ip_address)
    
    if current_peer_count >= max_peer_count:
        status = 'unsuccessful peer'
        reason = 'too many peers'

    #UPDATE to check for version
    
    #UPDATE make logic smoother
    elif peer != 'no peer found':
        if peer.status == 'local_contact_external_accepted':
            status = 'successful peer'
            reason = ''
            update_peer(ip_address=ip_address, port=port, status='connected')
            token = query_peer(ip_address=ip_address).peer_auth_key
        else:
            status = 'unsuccessful peer'
            reason = 'already exist as peer'
                
    else:
        status = 'successful peer'
        reason = ''
        token = str(add_peer(ip_address, port, 'external_contact_local_accepted'))
        #UPDATE version
        t1 = threading.Thread(target=responsive_peer_request,args=(1, peering_port, int(time.time()), ip_address, port,),daemon=True)
        t1.start()
    
    vars = namedtuple('vars', ['status','reason','token'])
    return vars(
        status,
        reason,
        token
    )
    

def authenticate_peer(ip_address, token):
    
    if query_peer(ip_address=ip_address) == 'no peer found':
        return False
    
    elif query_peer(ip_address=ip_address).peer_auth_key == token:
        return True
    
    else: 
        return False


def add_peer(ip_address,port,status):
    
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
def update_peer(ip_address,port="null",status="null",connected_time="null",last_ping="null",self_auth_key="null",peer_auth_key="null",derive_peer_auth_key=False):
    
    x = ''
    
    if port != "null":
        x = x + ",port = " + str(port) + " "
    if status != "null":
        x = x + ",status = '" + status + "' "
    if connected_time != "null":
        x = x + ",connected_time = '" + connected_time + "' "
    if last_ping != "null":
        x = x + ",last_ping = '" + last_ping + "' "
    if self_auth_key != "null":
        x = x + ",self_auth_key = '" + self_auth_key + "' "
    if peer_auth_key != "null":
        x = x + ",peer_auth_key = '" + peer_auth_key + "' "
    if derive_peer_auth_key == True:
        x = x + ",peer_auth_key = " + peer_auth_key + "uuid_generate_v1() "
    
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


def query_peer(ip_address = '', self_auth_key = '', peer_auth_key = ''):
    
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
        peers = columns(
                        peer_sql[0],
                        peer_sql[1],
                        peer_sql[2],
                        peer_sql[3],
                        peer_sql[4],
                        peer_sql[5],
                        peer_sql[6]
                        )

    except Exception as error:
        peers = 'no peer found'
    
    return peers 


def query_peers(ip_address = '', self_auth_key = '', peer_auth_key = ''):
    
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
    
    return peer_sql 


def peer_count():
    
    query = ('select count(*) from networking.peer')

    try:
        peer_count = executeSql(query)[0]

    except Exception as error:
        peer_count = 'no peer found'
    
    return peer_count


def delete_peer(ip_address):
    
    query = ("delete from networking.peer where ip_address = '" + ip_address +"';")
        
    try:
        delete = executeSqlDeleteUpdate(query)

    except Exception as error:
        print('error deleting' + str(error))
        delete = 'error deleting'
    
    return delete


def connect_to_peer(version, port, timestamp, peer_ip_address, peer_port):
    
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
    

def responsive_peer_request(version, port, timestamp, peer_ip_address, peer_port, wait_time=30):
    
    time.sleep(wait_time)
    
    peer_request = connect_to_peer(version, port, timestamp, peer_ip_address, peer_port)
    
    if peer_request.status == 'successful peer':
        update_peer(ip_address=peer_ip_address, self_auth_key=peer_request.token, status='connected')
        return 'Success'
    
    else:
        return 'Fail'    
    

def attempt_to_connect_to_new_peer(version, port, timestamp, peer_ip_address, peer_port):
    
    peer_request = connect_to_peer(version, port, timestamp, peer_ip_address, peer_port)
    
    if peer_request.status == 'successful peer':
        add_peer(peer_ip_address,peer_port,'local_contact_external_accepted')
        update_peer(ip_address=peer_ip_address, self_auth_key=peer_request.token)
        return 'Success'
    
    else:
        return 'Fail'
    
    
#UPDATE 
#add threading
#currently hardcoded to the structure of the peers query
#very inelegant with the post/get/etc rest type
#hardcoded auth
def message_all_connected_peers(endpoint, payload='', rest_type='get', peers_to_exclude=[]):

    peers = query_peers()
    
    responses = []
    
    print(peers)
    
    for i in range(0 ,len(peers)):
        exclude_peer = False
        peer_ip_address = peers[i][0]
        peer_port = peers[i][1]
        peer_status = peers[i][2]
        token = peers[i][5]

        for j in range(0,len(peers_to_exclude)):
            if peer_ip_address == peers_to_exclude[j]:
                exclude_peer = True
        
        if exclude_peer == False and peer_status == 'connected':
            url = "http://" + peer_ip_address + ":" + str(peer_port) + endpoint
            headers = {
                'Content-type': 'application/json', 
                'Accept': 'application/json', 
                'Authorization': token 
            }
            print(headers)
            
            if rest_type == 'get':
                print('trying get')
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
                
            responses.append([peer_ip_address,r])

    return responses


#UPDATE 
#currently hardcoded to the structure of the peers query
#very inelegant with the post/get/etc rest type
#hardcoded auth
def message_peer(endpoint, peer_ip_address, payload='', rest_type='get'):

    peer = query_peer(peer_ip_address)

    url = "http://" + peer_ip_address + ":" + str(peer.port) + endpoint
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'application/json', 
        'Authorization': peer.self_auth_key 
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
    
    print(r)

    return r

    
if __name__ == '__main__':
    
    #x = attempt_to_connect_to_new_peer(1, 8336, 1, '76.179.199.85', 8334)
    
    #connect_to_peer("abc", 100, 100, 'localhost' , 8334)
    #new_peer = add_peer('99.99.99.99',1000,'connected')
    #new_peer = add_peer('99.99.99.98',1000,'connected')
    #new_peer = add_peer('99.99.99.97',1000,'connected')
    #new_peer = add_peer('99.99.99.96',1000,'connected')

    #print(message_all_connected_peers(endpoint='abc',peers_to_exclude=['99.99.99.98']))
    
    #UNIT TESTS    
    '''
    new_peer = add_peer('99.99.99.99',1000,'initial_connection')
    print(query_peer(ip_address='') == 'no peer found')
    print(query_peer(ip_address='99.99.99.99').port == 1000)
    print(peer_count()==1)
    print(connect_peer('99.99.99.99',1, 1000, '11:00').status == 'unsuccessful peer')
    update_peer(ip_address='99.99.99.99',port=1006,status='xyz')
    print(query_peer(ip_address='99.99.99.99').port == 1006)
    delete_peer('99.99.99.99')
    print(query_peer(ip_address='99.99.99.99') == 'no peer found')
    print(authenticate_peer('99.99.99.98', 'abc')==False)
    '''
    