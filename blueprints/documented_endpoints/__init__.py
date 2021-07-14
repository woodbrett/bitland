'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import Blueprint
from flask_restplus import Api
from blueprints.documented_endpoints.hello_world import namespace as hello_world_ns
from blueprints.documented_endpoints.entities import namespace as entities_ns


blueprint = Blueprint('documented_api', __name__, url_prefix='/documented_api')

api_extension = Api(
    blueprint,
    title='Flask RESTplus Demo',
    version='1.0',
    description='Application tutorial to demonstrate Flask RESTplus extension\
        for better project structure and auto generated documentation',
    doc='/doc'
)

api_extension.add_namespace(hello_world_ns)
api_extension.add_namespace(entities_ns)
