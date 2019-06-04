#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import sys,os

import matplotlib.pyplot as plt
#get_ipython().magic(u'matplotlib inline')
plt.style.use('dark_background')

sys.path.append("..")
import pyrads

from scipy.integrate import trapz,simps,cumtrapz

### -----------------------------------
### Helpers
class Dummy:
    pass

### -----------------------------------


# In[ ]:



# ---
## setup thermodynamic parameters
params = Dummy()

params.Rv = pyrads.phys.H2O.R # moist component
params.cpv = pyrads.phys.H2O.cp
params.Lvap = pyrads.phys.H2O.L_vaporization_TriplePoint
params.satvap_T0 = pyrads.phys.H2O.TriplePointT
params.satvap_e0 = pyrads.phys.H2O.TriplePointP
params.esat = lambda T: pyrads.Thermodynamics.get_satvps(T,params.satvap_T0,params.satvap_e0,params.Rv,params.Lvap)

params.R = pyrads.phys.air.R  # dry component
params.cp = pyrads.phys.air.cp
params.ps_dry = 1e5           # surface pressure of dry component

params.g = 9.8             # surface gravity
params.cosThetaBar = 3./5. # average zenith angle used in 2stream eqns
params.RH = 0.8            # relative humidity

params.R_CO2 = pyrads.phys.CO2.R # non-condensible forcing component

# ---
## setup resolution (vertical,spectral)

#N_press = 15       # for testing only!
#dwavenr = 0.1     #  for testing only!

N_press = 18       # 
wavenr_min = 0.1   # [cm^-1]
wavenr_max = 3500. #
dwavenr = 0.1      # 

Tstrat = 150.      # stratospheric temperature

# ---
## setup range of temperatures, and if/where output is saved to:
Ts_vec = np.arange(250.,300.,2.)
CO2_vec = np.logspace(-6,-1,30)
CO2_vec = np.append(np.array([0]),CO2_vec)

### -----------------------------------
## MAIN LOOP

olr_spec_arr = np.zeros((CO2_vec.size,Ts_vec.size,np.int((wavenr_max-wavenr_min)/dwavenr)))
B_strat_arr = np.zeros((CO2_vec.size,Ts_vec.size,np.int((wavenr_max-wavenr_min)/dwavenr)))
B_surf_arr = np.zeros((CO2_vec.size,Ts_vec.size,np.int((wavenr_max-wavenr_min)/dwavenr)))

Ts_idx = 0
for Ts in Ts_vec:
    CO2_idx = 0
    for CO2_ppv in CO2_vec:
        
        print("wavenr_min,wavenr_max,dwave [cm^-1] = {0},{1},{2}".format(wavenr_min,wavenr_max,dwavenr))
        print("N_press = {0}".format(N_press))
        print("Surface temperature = {0} K".format(Ts))
        print("CO2 abundance = {0} ppv".format(CO2_ppv))

        # setup grid:
        g = pyrads.SetupGrids.make_grid( Ts,Tstrat,N_press,wavenr_min,wavenr_max,dwavenr,params, RH=params.RH )

        # compute optical thickness:
        #   -> this is the computationally most intensive step
        g.tau = pyrads.OpticalThickness.compute_tau_H2ON2_CO2dilute(g.p,g.T,g.q,CO2_ppv,g,params,RH=params.RH)
        
        # compute Planck functions etc:
        #   -> here: fully spectrally resolved!
        T_2D = np.tile( g.T, (g.Nn,1) ).T               # [press x wave]
        g.B_surf = np.pi* pyrads.Planck.Planck_n( g.n,Ts )     # [wave]
        g.B = np.pi* pyrads.Planck.Planck_n( g.wave, T_2D )    # [press x wave]

        # compute OLR etc:
        g.olr_spec = pyrads.Get_Fluxes.Fplus_alternative(0,g) # (spectrally resolved=irradiance)
        g.olr = simps(g.olr_spec,g.n)

        olr_spec_arr[CO2_idx,Ts_idx,:] = g.olr_spec 
        B_surf_arr[CO2_idx,Ts_idx,:] = g.B_surf
        B_strat_arr[CO2_idx,Ts_idx,:] = g.B[0,:]
        
        CO2_idx+=1
    Ts_idx+=1

np.savez(
    'output/olr_dense.npz',
    olr_spec = olr_spec_arr,
    B_surf = B_surf_arr,
    B_strat = B_strat_arr,
    n = g.n,
    Ts_vec = Ts_vec,
    CO2_vec = CO2_vec,
    Tstrat = Tstrat,
    RH = params.RH
)


# In[ ]:




