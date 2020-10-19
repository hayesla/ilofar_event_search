import matplotlib.pyplot as plt 
from read_bst_data import read_bst_data
from dynamic_spectra import dynamic_spectra
import glob
from matplotlib import dates


all_files = glob.glob('./bst_files/*.dat')
all_files.sort()

def plot_file(filename, background_sub=True, save_plot=None, **kwargs):

	spec_data, times, freq = read_bst_data(filename)

	dynamic_spec = dynamic_spectra(spec_data, times, freq)
	if background_sub:
		dynamic_spec = dynamic_spec.background_sub1()

	#plot the dynamic spectra
	fig, ax = plt.subplots(figsize=(10, 6))

	im = dynamic_spec.plot(**kwargs)

	ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

	fig.autofmt_xdate(rotation=45)
	plt.tight_layout()
	if save_plot is not None:
		plt.savefig(save_plot, dpi=200)
		plt.close()
	plt.show()

errors = []
for f in all_files:
	try:
		plot_file(f, 
			      save_plot='./all_plots/{:s}.png'.format(f.split('/')[-1][0:19]), 
			      cmap='Spectral_r')
		errors.append('pass')
	except:
		errors.append('error!')
