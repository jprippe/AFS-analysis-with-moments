#!/usr/bin/env python

# simple "primary contact"
# split, same size but two migration epochs in each pop, symmetric migration in first epoch, none in second epoch
# genomic islands
# n(para): 8


import matplotlib
matplotlib.use('PDF')
import moments
import pylab
import random
import matplotlib.pyplot as plt
import numpy as np
from numpy import array
from moments import Misc,Spectrum,Numerics,Manips,Integration,Demographics1D,Demographics2D
import sys
infile=sys.argv[1]
pop_ids=[sys.argv[2],sys.argv[3]]
projections=[int(sys.argv[4]),int(sys.argv[5])]
#params=[float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8]),float(sys.argv[9]),float(sys.argv[10]),float(sys.argv[11])]
params=[1,1,1,1,1,1,0.5,0.01]

# mutation rate per sequenced portion of genome per generation: for A.millepora, 0.02
mu=float(sys.argv[6])
# generation time, in thousand years: 0.005  (5 years)
gtime=float(sys.argv[7]) 

# set Polarized=False below for folded AFS analysis
fs = moments.Spectrum.from_file(infile)
data=fs.project(projections)
ns=data.sample_sizes
np.set_printoptions(precision=3)     

#-------------------
# split into unequal pop sizes with asymmetrical migration

def sc1il(params , ns):
#    p_misid: proportion of misidentified ancestral states
    nu1_1, nu2_1, T0, T, m,mi, P, p_misid = params
    sts = moments.LinearSystem_1D.steady_state_1D(ns[0] + ns[1])
    fs = moments.Spectrum(sts)
    fs = moments.Manips.split_1D_to_2D(fs, ns[0], ns[1])
    fs.integrate([nu1_1, nu2_1], T0, m = np.array([[0, m], [m, 0]]))
    fs.integrate([nu1_1, nu2_1], T, m = np.array([[0, 0], [0, 0]]))

    stsi = moments.LinearSystem_1D.steady_state_1D(ns[0] + ns[1])
    fsi = moments.Spectrum(stsi)
    fsi = moments.Manips.split_1D_to_2D(fsi, ns[0], ns[1])
    fsi.integrate([nu1_1, nu2_1], T0, m = np.array([[0, mi], [mi, 0]]))
    fsi.integrate([nu1_1, nu2_1], T, m = np.array([[0, 0], [0, 0]]))

    fs2=P*fsi+(1-P)*fs
    return (1-p_misid)*fs2 + p_misid*moments.Numerics.reverse_array(fs2)
 
func=sc1il
upper_bound = [100, 100, 100, 100, 200,200,0.999,0.25]
lower_bound = [1e-3,1e-3,1e-3,1e-3,1e-5,1e-5,0.001,1e-5]
params = moments.Misc.perturb_params(params, fold=2, upper_bound=upper_bound,
                              lower_bound=lower_bound)

poptg = moments.Inference.optimize_log(params, data, func,
                                   lower_bound=lower_bound,
                                   upper_bound=upper_bound,
                                   verbose=False, maxiter=30)

# extracting model predictions, likelihood and theta
model = func(poptg, ns)
ll_model = moments.Inference.ll_multinom(model, data)
theta = moments.Inference.optimal_sfs_scaling(model, data)

# random index for this replicate
ind=str(random.randint(0,999999))

# plotting demographic model
plot_mod = moments.ModelPlot.generate_model(func, poptg, ns)
moments.ModelPlot.plot_model(plot_mod, save_file="sc1iesm_"+ind+".png", pop_labels=pop_ids, nref=theta/(4*mu), draw_scale=False, gen_time=gtime, gen_time_units="KY", reverse_timeline=True)

# bootstrapping for SDs of params and theta

# printing parameters and their SDs
print( "RESULT","sc1iesm",ind,len(params),ll_model,sys.argv[1],sys.argv[2],sys.argv[3],poptg,theta)
                                    
# plotting quad-panel figure witt AFS, model, residuals:
moments.Plotting.plot_2d_comp_multinom(model, data, vmin=0.1, resid_range=3,
                                    pop_ids =pop_ids)
plt.savefig("sc1iesm_"+ind+"_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]+"_"+sys.argv[4]+"_"+sys.argv[5]+'.pdf')

