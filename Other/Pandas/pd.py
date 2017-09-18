import pandas as pd

a = pd.DataFrame({'col1':[1,2,3], 'col2':[3,4,5], 'col3':[6,7,8]})
print(a)
#a = a.append(pd.DataFrame({'col1':[4]}), ignore_index=True)
#print(a)

print(a.loc[0:1,'col1':'col2'])


