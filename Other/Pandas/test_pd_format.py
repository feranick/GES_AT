import pandas as pd
dfJV = pd.DataFrame({'V':[1,2,3], 'J':[4,5,6]})
dfJV = dfJV[['V', 'J']]
print(dfJV)
listJV0 = dict(dfJV.to_dict(orient='split'))
listJV0['columnlabel'] = listJV0.pop('columns')
listJV0['output'] = listJV0.pop('data')
del listJV0['index']

jsonData = {'itemId':'deviceID'}
jsonData.update(listJV0)
print(jsonData)

