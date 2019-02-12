import sympy, scipy
from scipy import special
import numpy as np

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
    #symSolutions['V_max'] = V_max.subs(zip(modelConstants,valuesForConstants))
    #symSolutions['P_max'] = P_max.subs(zip(modelConstants,valuesForConstants))
symSolutions['I'] = symSolutionsNoSubs['I'].subs(zip(modelConstants,valuesForConstants))
symSolutions['I0'] = symSolutionsNoSubs['I0'].subs(zip(modelConstants,valuesForConstants))
symSolutions['n'] = symSolutionsNoSubs['n'].subs(zip(modelConstants,valuesForConstants))
symSolutions['V'] = symSolutionsNoSubs['V'].subs(zip(modelConstants,valuesForConstants))
    
results = {}
results['symSolutions'] = symSolutions
results['modelSymbols'] = modelSymbols
results['modelVariables'] = modelVariables
print(results)
#return results
#============================

#symSolutions = results['symSolutions']
#modelSymbols = results['modelSymbols']
#modelVariables = results['modelVariables']
#self.isFastAndSloppy = results['beFastAndSloppy']

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

print(slns['V'])
print(slns['I'])

#self.readyForAnalysis = True
#print('Ready for analysis. F&S mode =',self.isFastAndSloppy)
#return slns
