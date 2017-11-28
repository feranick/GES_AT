'''
import csv
with open("test.txt") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ')
    for row in spamreader:
         print(', '.join(row))

'''
import numpy as np
PV = np.genfromtxt('test.txt', delimiter='\t')

Jpmax = np.amin(PV[np.where(PV[:,0]>0)][:,1])
Vpmax = PV[np.where(PV[:,0]>0)][np.argmin(PV[np.where(PV[:,0]>0)][:,1]),0]

print(Vpmax, Jpmax)
