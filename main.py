'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import Flask
from blueprints.peer import blueprint as peer
from blueprints.local import blueprint as local
import threading
from mining.mining_functions import miningProcess
from system_variables import (
    peering_port,
    peering_host,
    run_node_var,
    run_mining_var,
    initial_synch_var 
    )
from node.processing.synching import (
    start_node,
    run_node, initialSynch
    )
import time
import requests

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False

app.register_blueprint(peer)
app.register_blueprint(local)


def start_up():
    
    t4 = threading.Thread(target=ongoing_functions, daemon=True)
    t4.start()

    return None


def flask_started():
    
    not_started = True

    while not_started:
        print('waiting for flask to start')
        try:
            r = requests.get('http://localhost:' + str(peering_port) + '/peer/peering/ping/')
            print(r.status_code)
            if r.status_code in [200,401,404]:
                print('Server started, quitting start_loop')
                not_started = False
            print(r.status_code)
        except:
            print('Server not yet started')
        time.sleep(2)


def ongoing_functions():
    
    flask_started()

    if initial_synch_var == True:
        
        t3 = threading.Thread(target=run_node,args=(True,),daemon=True)
        t3.start()
        print('starting node', flush=True)
    
    else:    
        
        #start node ongoing functions (managing peers, pinging, garbage collecting transactions)
        if run_node_var == True:
            start_node()
            t1 = threading.Thread(target=run_node,daemon=True)
            t1.start()
            print('starting node', flush=True)
            
        #start mining if true
        if run_mining_var == True:
            t2 = threading.Thread(target=miningProcess,daemon=True)
            t2.start()
            print('started mining', flush=True)
    
    return None


if __name__ == "__main__":

    start_up()
    app.run(port=peering_port,host=peering_host)
    
   
    
    
    
    
