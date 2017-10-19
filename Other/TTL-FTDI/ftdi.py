import ftd2xx, time
'''
device = ftd2xx.listDevices()
ftd2xx.createDeviceInfoList()
print(ftd2xx.getDeviceInfoDetail(0,True))
print(device)

print("VID, PID: ",ftd2xx.getVIDPID())
'''
h = ftd2xx.open(0)
'''
print (h)
print("getDeviceInfo: ",h.getDeviceInfo)
print("getStatus: ",h.getStatus())
print("getBitMode: ",h.getBitMode())
'''
h.setTimeouts(1000,1000)

time.sleep(1)
print("5V :")
h.clrRts()

time.sleep(1)
print("0V :")
h.setRts()

time.sleep(2)

print("5V :")
h.clrRts()

h.close()
