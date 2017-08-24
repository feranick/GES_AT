import numpy as np

#a = np.array([])
a = np.zeros((1,5,5))
print(a)
print(a.shape)

b = np.vstack([a,a])
print(b)
print(b.shape)

b1 = np.stack([a,[1,1,1,1,1]], axis = 2)
print(b1)
print(b1.shape)
