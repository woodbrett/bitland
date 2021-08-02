'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import Flask
from blueprints.peer import blueprint as peer
from blueprints.local import blueprint as local
import threading
from mining.mining_functions import mining_process
from system_variables import (
    peering_port,
    peering_host
    )
from node.processing.synching import start_node

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False

app.register_blueprint(peer)
app.register_blueprint(local)
    
#start node ongoing functions (managing peers, pinging, garbage collecting transactions)
run_node = False
if run_node == True:
    t1 = threading.Thread(target=start_node,daemon=True)
    t1.start()
    print('starting node', flush=True)
    
#start mining if true
run_mining = False
if run_mining == True:
    t2 = threading.Thread(target=mining_process,daemon=True)
    t2.start()
    print('started mining', flush=True)


if __name__ == "__main__":
    
    app.run(port=peering_port,host=peering_host)
    
    #local_app.run(port=peering_port)
    #t1 = threading.Thread(target=local_app.run,args=(peering_port,),daemon=True)
    #t1.start()
    
    
