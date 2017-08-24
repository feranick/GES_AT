import numpy as np

#a = np.array([])
a = np.zeros((1,1,5))
print(a)
print(a.shape)

b = np.array([1,1,1,1,1])
print(b)
print(b.shape)

c = np.vstack([a,[[b]]])
print(c)
print(c.shape)

