import numpy as np
import pandas as pd
import json

np0 = np.array(['sample'])
np1 = np.array([[1,2,3,4,5],[1,4,9,16,25]]).T
np2 = np.array([7,8,9,10])

#print("np0\n",np0)
#print("np1\n",np1)
#print("np2\n",np2)


dftot = pd.DataFrame({'sample':np0, 'Voc': np2[1], 'Jsc':np2[0], 'MPP':np2[3]})
dfJV = pd.DataFrame({'V':np1[:,0], 'J':np1[:,1]})
pd.concat([dftot,dfJV], axis = 1).to_csv("test.csv", sep=',', index=False)

list1 = dict(dftot.to_dict(orient='list'))
list2 = dict(dfJV.to_dict(orient='list'))

list1.update(list2)
print(list1)
js1 = json.dumps(list1)
print(js1)


