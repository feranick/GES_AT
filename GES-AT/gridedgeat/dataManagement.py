'''
dataManagement.py
-------------
Class for providing access to data-management database

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys, math, json, os.path, time
global MongoDBhost

def main():
    if len(sys.argv)<3 or os.path.isfile(sys.argv[2]) == False:
        print(__doc__)
        print(' Usage:\n  python3 GridEdge_EnvMonitor_class.py <lab-identifier> <mongoFile>\n')
        return
    
    lab = sys.argv[1]
    mongoFile = sys.argv[2]

    sensData = []
    #sensData.extend([conc, conc_aqi])
    
    #************************************
    ''' Make JSON and push to MongoDB '''
    #************************************
    conn = GEmongoDB(sensData,mongoFile)
    #print(" JSON:\n",conn.makeJSON(),"\n")

    print(" Pushing to MongoDB:")
    try:
        conn.pushToMongoDB()
        print(" Submission to MongoDB successful\n")
    except:
        print(" Submission to MongoDB failed\n")

#************************************
''' Class Database '''
#************************************
class DataManagementDB:
    def __init__(self, info):
        #self.info = info
        self.dbHostname = info[0]
        self.dbPortNum = info[1]
        self.dbName = info[2]
        self.dbUsername = info[3]
        self.dbPassword = info[4]

    def connectDB(self):
        from pymongo import MongoClient
        client = MongoClient(self.dbHostname, int(self.dbPortNum))
        auth_status = client[self.dbName].authenticate(self.dbUsername, self.dbPassword, mechanism='SCRAM-SHA-1')
        print(' Authentication status = {0} \n'.format(auth_status))
        return status, client

    def printAuthInfo(self):
        print(self.dbHostname)
        print(self.dbPortNum)
        print(self.dbName)
        print(self.dbUsername)
        print(self.dbPassword)

    def makeJSON(self):
        dataj = {
            'hostname' : self.dbHostname,
            'IP' : self.data[1],
            'self.dbName' : info[2],
            }
        return json.dumps(dataj)

    def pushToMongoDB(self):
        jsonData = self.makeJSON()
        client = self.connectDB()
        db = client.Tata
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(jsonData))
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")


