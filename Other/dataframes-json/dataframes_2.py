import numpy as np
import pandas as pd
import json

np0 = np.zeros((0,1))
np_new0 = np.array(['sample'])
np0 = np.vstack((np0,np_new0))
print("np_new0\n",np_new0)
print("np0\n",np0)

np1 = np.zeros((5,2))
print("np1\n",np1)
np_new1 = np.array([[1,1],[2,4],[3,9],[4,16],[5,25]])
print("np_new1\n",np_new1[:,:])
np1 = np.vstack((np1,np_new1))
print("np1\n",np1)

np2 = np.zeros((0,4))
np_new2 = np.array([7,8,9,10])
np2 = np.vstack((np2,np_new2))

print("np_new2\n",np_new2)
print("np2\n",np2)


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

