from sunpy.net import Fido, attrs as a 
from sunpy import timeseries as ts 
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd 

from read_bst_data import read_bst_data

def plot_event(tstart, tend, plot_goes=False):
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