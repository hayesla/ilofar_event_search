from sunpy.net import Fido, attrs as a 
from sunpy import timeseries as ts 
from sunpy.time import parse_time
import glob
import matplotlib.pyplot as plt
from matplotlib import dates
import numpy as np
import pandas as pd 
from read_bst_data import read_bst_data
from dynamic_spectra import dynamic_spectra
from pathlib import Path
import os 

def plot_event(tstart, tend, path="./bst_files/", 
			   plot_goes=False, goes_path="./goes_files/",
			   background_sub=False, save_plot=None, **kwargs):
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
		tstart = parse_time(tstart).datetime
	if isinstance(tend, str):
		tend = parse_time(tend).datetime

	file = glob.glob(path+tstart.strftime("%Y%m%d*.dat"))
	if len(file)==0:
		return 

	spec_data, times, freq = read_bst_data(file[0])

	dynamic_spec = dynamic_spectra(spec_data, times, freq).crop_time(tstart, tend)
	if background_sub:
		dynamic_spec = dynamic_spec.background_sub1()

	if plot_goes:
		goes_file = Path(goes_path + tstart.strftime("go15%Y%m%d.fits"))
		if goes_file.exists():
			goes_ts = ts.TimeSeries(os.fspath(goes_file)).truncate(tstart, tend)
		else:
			try:
				goes_file = get_goes(tstart, tend)
				goes_ts = ts.TimeSeries(goes_file).truncate(tstart, tend)
			except:
				print("cant get GOES XRS data")
				return

	fig, ax = plt.subplots(figsize=(10, 6))

	im = dynamic_spec.plot(**kwargs)

	if plot_goes:
		ax2 = ax.twinx()
		ax2.plot(goes_ts.to_dataframe()["xrsb"], color="k", label="1-8 $\mathrm{\AA}$")
		ax2.plot(goes_ts.to_dataframe()["xrsa"], color="k", ls="dashed", label="0.5-4 $\mathrm{\AA}$")
		ax2.set_ylabel("Flux Wm$^{-2}$")
		ax2.set_yscale("log")
		ax2.legend(loc='lower right')
		ax2.set_ylim(1e-9, 1e-3)


	ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

	#fig.colorbar(im)
	fig.autofmt_xdate(rotation=45)
	plt.tight_layout()
	if save_plot is not None:
		plt.savefig(save_plot, dpi=200)
		plt.close()
	plt.show()


def get_goes(tstart, tend, path="./goes_files/"):
	res = Fido.search(a.Time(tstart, tend), a.Instrument("XRS"), a.goes.SatelliteNumber(15))
	f = Fido.fetch(res, path=path)
	return f



def run_for_all_events():
	events = pd.read_csv("lofar_flare_event_candidates.csv")
	errors = []
	for i in range(len(events)):
		try:
			plot_event(events.iloc[i]["event_starttime"], events.iloc[i]["event_endtime"],
				   plot_goes=True, background_sub=True, cmap="Spectral_r",
				   save_plot="./plots/quicklook_{:s}.png".format(events.iloc[i]["event_starttime"]))
			errors.append("worked")
		except:
			print(i)
			errors.append("failed")

failed = np.array([ 0,  1,  7, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 45,
       46, 47, 49, 50, 51, 53, 54, 55, 56, 64, 69, 70, 71, 74, 79, 81, 85,
       86, 89, 90])

def redo_failed():
	events = pd.read_csv("lofar_flare_event_candidates.csv")
	for i in failed:
		try:
			plot_event(events.iloc[i]["event_starttime"], events.iloc[i]["event_endtime"],
				   plot_goes=True, background_sub=True, cmap="Spectral_r",
				   save_plot="./plots/quicklook_{:s}.png".format(events.iloc[i]["event_starttime"]))
		except:
			print(i)

def test_failed(i):
	events = pd.read_csv("lofar_flare_event_candidates.csv")
	tstart = events.iloc[i]['event_starttime']
	tend = events.iloc[i]['event_endtime']

	if isinstance(tstart, str):
		tstart = parse_time(tstart).datetime
	if isinstance(tend, str):
		tend = parse_time(tend).datetime
	path='./bst_files/'
	file = glob.glob(path+tstart.strftime("%Y%m%d*.dat"))
	if len(file)==0:
		print('no file')
	if len(file)!=0:
		
		try:
			spec_data, times, freq = read_bst_data(file[0])
			if tstart < times[-1] or tend < times[0] :
				print(i)
				print('reason truncate!')
			else:
				print('trying!')
				plot_event(events.iloc[i]["event_starttime"], events.iloc[i]["event_endtime"],
				   plot_goes=True, background_sub=True, cmap="Spectral_r",
				   save_plot="./plots/quicklook_{:s}.png".format(events.iloc[i]["event_starttime"]))	
		except:
			print('other reason!', i)

		#dynamic_spec = dynamic_spectra(spec_data, times, freq).crop_time(tstart, tend)



