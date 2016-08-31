'''
This module contains helper functions for timedata classes.
'''

import numpy as np
import pandas as pd

from scipy.interpolate import interp1d

#function to ensure all arrays are of length nt
def _assert_lent(array, nt):
	'''
	Helper function to ensure all arrays are of length nt.

	Parameters
	----------
	array : scalar or array-like
		Array to ensure is length nt. If scalar, returns array of repeated
		scalar value.

	nt : int
		Length of array to ensure

	Returns
	-------
	array : np.ndarray
		Array of length nt.

	Raises
	------
	TypeError
		If `array` is not scalar or array-like.

	TypeError
		If `nt` is not int.

	ValueError
		If `array` is array-like but not of length nt.

	'''

	#check nt is int
	if not isinstance(nt, int):
		raise TypeError('nt must be int')

	#ensure array is the right length
	if isinstance(array, (int, float)):
		return array*np.ones(nt)

	elif isinstance(array, (list, np.ndarray)):
		if len(array) != nt:
			raise ValueError('array must have length nt')

		return np.array(array)
	
	else:
		raise TypeError('array bust be scalar, array-like, or None')

#function to numerically derivatize an array wrt another array
def _derivatize(num, denom):
	'''
	Helper function to calculate derivatives.

	Parameters
	----------
	num : scalar or array-like
		Numerator of derivative function, length nt.

	denom : array-like
		Denominator of derivative function, length nt. Returns array of zeros
		if `denom` is not continuously increasing.

	Returns
	-------
	dndd : np.ndarray
		Derivative of `num` wrt `denom`. Returns an array of zeros of
		length nt if `num` is a scalar or if `denom` is not continuously
		increasing.

	Raises
	------
	TypeError
		If `num` is not scalar or array-like.
	
	TypeError
		If `denom` is not array-like.

	ValueError
		If `num` and `denom` are both array-like but have different lengths.
	'''

	#check inputted data types and raise appropriate errors
	if not isinstance(num, (int, float, list, np.ndarray)):
		raise TypeError('num bust be scalar or array-like')

	elif not isinstance(denom, (list, np.ndarray)):
		raise TypeError('denom bust be array-like')

	#take gradients, and clean-up if necessary
	try:
		dn = np.gradient(num)
	except ValueError:
		dn = np.zeros(len(denom))

	dd = np.gradient(denom)

	#check lengths and continuously increasing denom
	if len(dn) != len(dd):
		raise ValueError('num and denom arrays must have same length')

	elif any(dd) <= 0:
		return np.zeros(len(denom))

	return np.array(dn/dd)

#define function to extract variables from .csv file
def _rpo_extract_tg(file, nt, err):
	'''
	Extracts time, temperature, and carbon remaining vectors from `all_data`
	file generated by NOSAMS RPO LabView program (VERSION XXX).

	Parameters
	----------
	file : str or pd.DataFrame 
		File containing thermogram data, either as a path string or 
		``pd.DataFrame`` instance.

	nT : int 
		The number of time points to use. Defaults to 250.

	ppm_CO2_err : int or float
		The CO2 concentration standard deviation, in ppm. Used to 
		calculate `g_std`.

	Returns
	-------
	g : np.ndarray
		Array of the true fraction of carbon remaining at each timepoint.
		Length nt.

	g_std : np.ndarray
		Array of the standard deviation of `g`. Length nt.
	
	t : np.ndarray
		Array of timep, in seconds. Length nt.

	T : np.ndarray
		Array of temperature, in Kelvin. Length nt.

	Raises
	------
	TypeError
		If `file` is not str or ``pd.DataFrame`` instance.
	
	TypeError
		If index of `file` is not ``pd.DatetimeIndex`` instance.

	TypeError
		If `nt` is not int.

	ValueError
		If `file` does not contain "CO2_scaled" and "temp" columns.
	'''

	#check data format and raise appropriate errors
	if isinstance(file, str):
		#import as dataframe
		file = pd.read_csv(file,
			index_col=0,
			parse_dates=True)

	elif not isinstance(file, pd.DataFrame):
		raise TypeError('file must be pd.DataFrame instance or path string')

	if 'CO2_scaled' and 'temp' not in file.columns:
		raise ValueError('file must have "CO2_scaled" and "temp" columns')

	elif not isinstance(file.index, pd.DatetimeIndex):
		raise TypeError('file index must be pd.DatetimeIndex instance')

	#extract necessary data
	secs = (file.index - file.index[0]).seconds
	CO2 = file.CO2_scaled
	tot = np.sum(CO2)
	Temp = file.temp

	#calculate alpha and stdev bounds
	alpha = np.cumsum(CO2)/tot
	alpha_p = np.cumsum(CO2+err)/tot
	alpha_m = np.cumsum(CO2-err)/tot

	#generate t array
	t0 = secs[0]; tf = secs[-1]; dt = (tf-t0)/nt
	t = np.linspace(t0,tf,nt+1) + dt/2 #make downsampled points at midpoint
	t = t[:-1] #drop last point since it's beyond tf

	#generate functions to down-sample
	fT = interp1d(secs, Temp)
	fg = interp1d(secs, alpha)
	fg_p = interp1d(secs, alpha_p)
	fg_m = interp1d(secs, alpha_m)
	
	T = fT(t) + 273.15 #convert to K
	g = 1-fg(t)
	g_std = 0.5*(fg_p(t) - fg_m(t))
	
	return g, g_std, t, T










