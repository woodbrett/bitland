'''
Created on Nov 8, 2020

@author: brett_wood
'''
from configparser import ConfigParser
from system_variables import database_settings_file_location

def config(filename=database_settings_file_location, section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db