'''
Created on Dec 27, 2021

@author: postgres
'''
from system_variables import internet_connectivity_test_source
import requests

def checkInternetConnection():
    
    url = internet_connectivity_test_source
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        print("Connected to the Internet")
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("No internet connection.")
        return False

if __name__ == '__main__':
    
    checkInternetConnection()