# script to run thermogram deconvolution
import rampedpyrox as rp
import numpy as np
import os
import matplotlib.pyplot as plt


#function to load files
def gen_str(name):
	p = os.path.join(os.path.dirname(__file__), name)
	return p

#paths to data files
data = gen_str('test_data/TS1.csv') #REPLACE THIS WITH A PATH TO YOUR DATA
sum_data = gen_str('test_data/TS1_sum.csv') #REPLACE THIS WITH A PATH TO YOUR DATA

#calculate thermogram
tg = rp.RpoThermogram.from_csv(
	data,
	bl_subtract = True,
	nt=250)

#calculate DAEM
daem = rp.Daem.from_timedata(
	tg,
	log10k0=10, #value advocated in JDH thesis Ch 3
	E_max=400, #can change if too high
	E_min=50, #can change if too low
	nE=400)

#calculate energy complex
ec = rp.EnergyComplex.inverse_model(
	daem, 
	tg,
	omega=.05) #can replace with best-fit value if known

#forward model estimated thermogram back onto tg
tg.forward_model(daem, ec)

#calculate isotope results
ri = rp.RpoIsotopes.from_csv(
	sum_data,
	daem,
	ec,
	blk_corr = True,
	bulk_d13C_true = [-24.8, 0.1]) #REPLACE THIS WITH VALUE FOR EACH SAMPLE!!






