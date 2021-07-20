'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import Flask
from blueprints.basic_endpoints import blueprint as basic_endpoint
from blueprints.documented_endpoints import blueprint as documented_endpoint
from blueprints.peer import blueprint as peer
import threading
from mining.mining_functions import mining_process
from system_variables import (
    peering_port,
    peering_host
    )

app = Flask(__name__)
app.config['RESTPLUS_MASK_SWAGGER'] = False

app.register_blueprint(basic_endpoint)
app.register_blueprint(documented_endpoint)
app.register_blueprint(peer)

#start mining if true
run_mining = True
if run_mining == True:
    t2 = threading.Thread(target=mining_process,daemon=True)
    t2.start()
    print('started mining', flush=True)
    
#start node ongoing functions (managing peers, pinging, garbage collecting transactions)
run_node = False
#if run_node == True:
#    t3 = threading.Thread(target=mining_process,daemon=True)

if __name__ == "__main__":
    
    app.run(port=peering_port,host=peering_host)
    
    
