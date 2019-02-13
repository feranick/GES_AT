'''
diodeEquation.py
----------------
Classes for providing advanced fitting through the Diode Equation
for the resultsWindow

From: https://github.com/mutovis/analysis-software

Copyright (C) 2017-2019 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import numpy as np
import pandas as pd
import time, random, math
from lmfit import Model
from scipy import special
import sympy, scipy
from datetime import datetime
from PyQt5.QtWidgets import (QApplication,QAbstractItemView)
from PyQt5.QtCore import (Qt,QObject, QThread, pyqtSlot, pyqtSignal)

####################################################################
#   Diode Equation
####################################################################
class DiodeEquation(QThread):
    results = pyqtSignal(str)
    func = pyqtSignal(object)
    JV_fit = pyqtSignal(np.ndarray, np.ndarray)
    
    def __init__(self, parent=None):
        super(DiodeEquation, self).__init__(parent)

    def __del__(self):
        self.wait()
    
    def stop(self):
        self.terminate()

    def fitDE(self,cellEqn,JV):
        vv = JV[:,0]
        ii = JV[:,1]
        #cellEqn = self.setupEq()
        cellModel = Model(cellEqn,nan_policy='omit')
        cellModel.set_param_hint('n',value=1)
        cellModel.set_param_hint('Rs',value=6)
        cellModel.set_param_hint('Rsh',value=1e5)
        cellModel.set_param_hint('Iph',value=20e-3)
        cellModel.set_param_hint('I0',value=1e-9)
        fitResult = cellModel.fit(ii, V=vv)
        resultParams = fitResult.params
        self.results.emit(fitResult.fit_report())
        self.results.emit(fitResult.message)
        n = fitResult.best_values['n']
        Rs = fitResult.best_values['Rs']
        Rsh = fitResult.best_values['Rsh']
        Iph = fitResult.best_values['Iph']
        I0 = fitResult.best_values['I0']
        ii_fit = cellEqn(vv,n,Rs,Rsh,I0,Iph).real
        #print(ii_fit)
        self.JV_fit.emit(vv, ii_fit)

    def run(self):
        self.results.emit("Solving calculation for the diode equation. Please wait...")
        modelSymbols = sympy.symbols('I0 Iph Rs Rsh n I V Vth', real=True, positive=True)
        I0, Iph, Rs, Rsh, n, I, V, Vth = modelSymbols
        modelConstants = (Vth,)
        modelVariables = tuple(set(modelSymbols)-set(modelConstants))

        # calculate values for our model's constants now
        cellTemp = 29 #degC all analysis is done assuming the cell is at 29 degC
        T = 273.15 + cellTemp #cell temp in K
        K = 1.3806488e-23 #boltzman constant
        q = 1.60217657e-19 #electron charge
        thermalVoltage = K*T/q #thermal voltage ~26mv
        valuesForConstants = (thermalVoltage,)

        lhs = I
        rhs = Iph-((V+I*Rs)/Rsh)-I0*(sympy.exp((V+I*Rs)/(n*Vth))-1)
        electricalModel = sympy.Eq(lhs,rhs)
        #electricalModelVarsOnly= electricalModel.subs(zip(modelConstants,valuesForConstants))

        symSolutionsNoSubs = {} # all the symbols preserved
        solveForThese = [I, I0, V, n]
        for symbol in solveForThese:
            symSolutionsNoSubs[str(symbol)] = sympy.solve(electricalModel,symbol)[0]

        Voc_eqn = symSolutionsNoSubs['V'].subs(I,0) # analytical solution for Voc
        Isc_eqn = symSolutionsNoSubs['I'].subs(V,0) # analytical solution for Isc

        PB = symSolutionsNoSubs['V']*I # analytical solution for power (current as independant variable)
        P_primeB = sympy.diff(PB,I) # first derivative of power (WRT I)

        symSolutions = {}
        symSolutions['Isc'] = Isc_eqn.subs(zip(modelConstants,valuesForConstants))
        symSolutions['Voc'] = Voc_eqn.subs(zip(modelConstants,valuesForConstants))
        symSolutions['P_prime'] = P_primeB.subs(zip(modelConstants,valuesForConstants))
        symSolutions['I'] = symSolutionsNoSubs['I'].subs(zip(modelConstants,valuesForConstants))
        symSolutions['I0'] = symSolutionsNoSubs['I0'].subs(zip(modelConstants,valuesForConstants))
        symSolutions['n'] = symSolutionsNoSubs['n'].subs(zip(modelConstants,valuesForConstants))
        symSolutions['V'] = symSolutionsNoSubs['V'].subs(zip(modelConstants,valuesForConstants))

        results = {}
        results['symSolutions'] = symSolutions
        results['modelSymbols'] = modelSymbols
        results['modelVariables'] = modelVariables
        #print(results)

        I0, Iph, Rs, Rsh, n, I, V, Vth = modelSymbols

        # here we define any function substitutions we'll need for lambdification later
        #if self.isFastAndSloppy:
        # for fast and inaccurate math
        functionSubstitutions = {"LambertW" : scipy.special.lambertw, "exp" : np.exp, "log" : np.log}
        #functionSubstitutions = {"LambertW" : scipy.special.lambertw, "exp" : bigfloat.exp}
        #else:
        # this is a massive slowdown (forces a ton of operations into mpmath)
        # but gives _much_ better accuracy and aviods overflow warnings/errors...
        #functionSubstitutions = {"LambertW" : mpmath.lambertw, "exp" : mpmath.exp, "log" : mpmath.log}

        slns = {}
        solveForThese = [I, I0, V, n]
        for symbol in solveForThese:
            remainingVariables = list(set(modelVariables)-set([symbol]))
            slns[str(symbol)] = sympy.lambdify(remainingVariables,symSolutions[str(symbol)],functionSubstitutions,dummify=False)
            #slns[str(symbol)] = ufuncify(remainingVariables,self.symSolutions[str(symbol)],helpers=[['LambertW', sympy.LambertW(x), [x]]])
            #slns[str(symbol)] = functools.partial(tmp)
        
        slns['Voc'] = sympy.lambdify([I0,Rsh,Iph,n],symSolutions['Voc'],functionSubstitutions,dummify=False)
        slns['P_prime'] = sympy.lambdify([I0,Rsh,Iph,n,Rs,I],symSolutions['P_prime'],functionSubstitutions,dummify=False)
        slns['Isc'] = sympy.lambdify([I0,Rsh,Iph,n,Rs],symSolutions['Isc'],functionSubstitutions,dummify=False)
        
        #slns['I'] = sympy.lambdify([I0,Rsh,Iph,n,Rs,V],symSolutions['I'],functionSubstitutions,dummify=False)
        slns['I'] = sympy.lambdify([V,n,Rs,Rsh,I0,Iph],symSolutions['I'],functionSubstitutions,dummify=False)
        
        #slns['V'] = sympy.lambdify([I0,Rsh,Iph,n,Rs,I],symSolutions['I'],functionSubstitutions,dummify=False)
        #print(slns['I'](1,2,3,4,5,vv))
        #print(slns['V'](1,2,3,4,5,ii))
        self.results.emit(" Setup DE: Completed")
        #return slns['I']
        self.func.emit(slns['I'])

