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
            'lab' : self.data[0],
            'IP' : self.data[1],
            'date' : self.data[2],
            'time' : self.data[3],
            'temperature' : '{0:0.1f}'.format(self.data[4]),
            'pressure' : '{0:0.1f}'.format(self.data[5]),
            'humidity' : '{0:0.1f}'.format(self.data[6]),
            'PM2.5_particles_L' : '{0:0.2f}'.format(self.data[7]),
            'aqi' : '{0:0d}'.format(int(self.data[8])),
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


