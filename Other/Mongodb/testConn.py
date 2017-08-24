#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
**********************************************************
*
* GridEdge - Environmental Tracking - using classes
* version: 20170726b
*
* By: Nicola Ferralis <feranick@hotmail.com>
*
***********************************************************
'''
#print(__doc__)

import sys, math, json, os.path, time


global MongoDBhost

def main():
    mongoFile = sys.argv[1]
    
    #************************************
    ''' Read from T/RH sensor '''
    #************************************
    #trhSensor = TRHSensor(lab)
    #sensData = trhSensor.readSensors()
    #trhSensor.printUI()
    sensData = ['test', 'Nicola']
    
    #************************************
    ''' Make JSON and push to MongoDB '''
    #************************************
    conn = GEmongoDB(sensData,mongoFile)
    print("\n JSON:\n",conn.makeJSON(),"\n")
    print(" Pushing to MongoDB:")
    conn.pushToMongoDB()

#************************************
''' Class Database '''
#************************************
class GEmongoDB:
    def __init__(self, data, file):
        self.data = data
        with open(file, 'r') as f:
            f.readline()
            self.hostname = f.readline().rstrip('\n')
            f.readline()
            self.port_num = f.readline().rstrip('\n')
            f.readline()
            self.dbname = f.readline().rstrip('\n')
            f.readline()
            self.username = f.readline().rstrip('\n')
            f.readline()
            self.password = f.readline().rstrip('\n')

    def connectDB(self):
        from pymongo import MongoClient
        client = MongoClient(self.hostname, int(self.port_num))
        print(client[self.dbname])
        print(client.test)
        auth_status = client[self.dbname].authenticate(self.username, self.password, mechanism='SCRAM-SHA-1')
        print(' Authentication status = {0} \n'.format(auth_status))
        return client

    def printAuthInfo(self):
        print(self.hostname)
        print(self.port_num)
        print(self.dbname)
        print(self.username)
        print(self.password)

    def makeJSON(self):
        dataj = {
            'test-submit' : self.data[0],
            'name' : self.data[1],
            }
        return json.dumps(dataj)
    
    def pushToMongoDB(self):
        jsonData = self.makeJSON()
        client = self.connectDB()
        db = client[self.dbname]
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(jsonData))
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")


#************************************
''' Get system IP '''
#************************************
def getIP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
