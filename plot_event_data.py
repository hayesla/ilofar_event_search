from sunpy.net import Fido, attrs as a 
from sunpy import timeseries as ts 
from sunpy.time import parse_time
import glob
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd 
from read_bst_data import read_bst_data
from dynamic_spectra import dynamic_spectra

def plot_event(tstart, tend, path='./bst_files/',plot_goes=False):
	"""
	Function to plot the dynamic spectrum for a given date.

	Parameters
	----------
	tstart : ~`datetime.datetime`, ~`str`
		start time 
	tend : ~`datetime.datetime`, ~`str`
		end time
	plot_goes : ~`boolean`, optional
		if True overplot the GOES XRS lightcurves
	"""

	if isinstance(tstart, str):
		tstart = parse_time(tstart)
	if isinstance(tend, str):
		tend = parse_time(tend)

	file = glob.glob(path+tstart.strftime('%Y%m%d*.dat'))
	if len(file)==0:
		return 

	spec_data, times, freq = read_bst_data(file[0])

	dynamic_spec = dynamic_spectra(spec_data, times, freq).crop_time(tstart, tend)

	return dynamic_spec

