'''
Created on Sep 8, 2021

@author: admin
'''
from datetime import datetime, timezone

def getTimeNowSeconds():

    return int(round(datetime.now(timezone.utc).timestamp(),0))


if __name__ == "__main__":

    print(getTimeNowSeconds())