'''
dataManagement.py
-----------------
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

#************************************
''' Class Database '''
#************************************
class DataManagement:
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
        if self.dbUsername != "" and self.dbPassword !="":
            client[self.dbName].authenticate(self.dbUsername, self.dbPassword)
        else:
            client[self.dbName]
        try:
            client.admin.command('ismaster')
            print(" Server Available!")
            flag = True
        except:
            print(" Server not available")
            flag = False
        return client, flag

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
        client,_= self.connectDB()
        db = client[self.dbName]
        try:
            db_entry = db.EnvTrack.insert_one(json.loads(jsonData))
            print(" Data entry successful (id:",db_entry.inserted_id,")\n")
        except:
            print(" Data entry failed.\n")


