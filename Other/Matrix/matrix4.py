import numpy as np

#a = np.array([])
a = np.zeros((0,1,5))
#print(a)
#print(a.shape)

b1 = np.array([1,1,1,1,1])
b2 = np.array([2,2,2,2,2])
b3 = np.array([3,3,3,3,3])
b4 = np.array([4,4,4,4,4])
b5 = np.array([5,5,5,5,5])


#print(b)
#print(b.shape)

c0 = np.insert(a,0,b1,axis= 0)
print(c0)
print(c0.shape)

c0 = np.insert(c0,c0.shape[0]-1,2,axis= 1)
print(c0)
print(c0.shape)

c0 = np.insert(c0,c0.shape[0]-1,b3,axis= 1)
print(c0)
print(c0.shape)

c0 = np.insert(c0,0,b4,axis= 0)
print(c0)
print(c0.shape)

c0 = np.insert(c0,0,b5,axis= 0)
print(c0)
print(c0.shape)

c0 = np.insert(c0,c0.shape[0],b3,axis= 1)
print(c0)
print(c0.shape)
