#!/usr/bin/env python

# growth before split, two epochs in each pop, NO migration
# n(para): 9


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
params=[1,1,1,1,1,1,1,1,0.01]

# mutation rate per sequenced portion of genome per generation: for A.millepora, 0.02
mu=float(sys.argv[6])
# generation time, in thousand years: 0.005  (5 years)
gtime=float(sys.argv[7]) 

dd = Misc.make_data_dict(infile)
# set Polarized=False below for folded AFS analysis
data = Spectrum.from_data_dict(dd, pop_ids,projections,polarized=True)
ns=data.sample_sizes
np.set_printoptions(precision=3)     

#-------------------
# split into unequal pop sizes with asymmetrical migration

def sc12nm(params , ns):
#    p_misid: proportion of misidentified ancestral states
    nu0, nu1_2,nu2_2,nu1_3,nu2_3,T1, T2, T3,p_misid = params

    sts = moments.LinearSystem_1D.steady_state_1D(ns[0] + ns[1])
    fs = moments.Spectrum(sts)
    fs.integrate([nu0], T1)
    fs = moments.Manips.split_1D_to_2D(fs, ns[0], ns[1])
    fs.integrate([nu1_2, nu2_2], T2, m = np.array([[0, 0], [0, 0]]))
    fs.integrate([nu1_3, nu2_3], T3, m = np.array([[0, 0], [0, 0]]))

    return (1-p_misid)*fs + p_misid*moments.Numerics.reverse_array(fs)
 
func=sc12nm
upper_bound = [100, 100,100,100, 100, 100, 100,100,0.25]
lower_bound = [1e-8, 1e-8,1e-8,1e-8,1e-8,1e-8,1e-8,1e-8,1e-5]
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
moments.ModelPlot.plot_model(plot_mod, save_file="sc12nm_"+ind+".png", pop_labels=pop_ids, nref=theta/(4*mu), draw_scale=False, gen_time=gtime, gen_time_units="KY", reverse_timeline=True)

# bootstrapping for SDs of params and theta
all_boot=moments.Misc.bootstrap(dd,pop_ids,projections)
uncert=moments.Godambe.GIM_uncert(func,all_boot,poptg,data)

# printing parameters and their SDs
print "RESULT","sc12nm",ind,len(params),ll_model,sys.argv[1],sys.argv[2],sys.argv[3],poptg,theta,uncert
                                    
# plotting quad-panel figure witt AFS, model, residuals:
moments.Plotting.plot_2d_comp_multinom(model, data, vmin=1, resid_range=3,
                                    pop_ids =pop_ids)
plt.savefig("sc12nm_"+ind+"_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]+"_"+sys.argv[4]+"_"+sys.argv[5]+'.pdf')

