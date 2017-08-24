import numpy as np
import pandas as pd
import json

np1 = np.array([10,20,30,40])
np2 = np.array([1,2,3,4])
print("np2\n",np2)
np_new2 = np.array([7,8,9,10])
print(np2.shape, np_new2.shape)
print("np_new2\n",np_new2)
np2 = np.vstack((np2,np_new2))
np2 = np.vstack((np2,np_new2))
print("np2\n",np2)
np3 = np.vstack((np_new2,np2))

dftot = pd.DataFrame({'dev1':[np2], 'dev2':[np2]})

dftot.get_value(0,'dev1')

print(dftot)
print(dftot.get_value(0,'dev1'))

#dftot['dev3'] = [np2]
#print(dftot)

df1 = pd.DataFrame({'dev1': [np1]})
print(df1)
dftot2 = dftot.append(df1)
print(dftot2)


'''
np1 = np.zeros((5,2))
print("np1\n",np1)
np_new1 = np.array([[1,1],[2,4],[3,9],[4,16],[5,25]])
print(np1.shape, np_new1.shape)
print("np_new1\n",np_new1)
np1 = np.vstack((np1[:0],np_new1))
np1 = np.stack((np1,np_new1))

print("np1\n",np1)
print(np1.shape)

print(np1[0])

'''




'''
dftot = pd.DataFrame({'sample':np0[0], 'Voc': np2[0,1], 'Jsc':np2[0,0], 'MPP':np2[0,3]})
dfJV = pd.DataFrame({'V':np1[0,:,0], 'J':np1[0,:,1]})
pd.concat([dftot,dfJV], axis = 1).to_csv("test.csv", sep=',', index=False)

list1 = dict(dftot.to_dict(orient='list'))
list2 = dict(dfJV.to_dict(orient='list'))

list1.update(list2)
print(list1)
js1 = json.dumps(list1)
print(js1)
'''

