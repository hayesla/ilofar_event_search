import pandas as pd 
from sunpy.time import parse_time
import numpy as np 
from copy import copy
import matplotlib.pyplot as plt 
from matplotlib import dates
from astropy import units as u 
    
class dynamic_spectra():
    """
    A dynamic spectrogram class. The idea is to for this to be a container
    for dynamic spectra which can then be truncated etc. 

    Parameters
    ----------
    data : `~np.ndarray`
        2D spectrogram data.
    times : `~np.ndarray`
        1D array of times associated with spectrogram.
    freq : `~np.ndarray`
        1D array of frequencies associated with spectrogram.

    Examples
    --------
    >>> my_spec = dyanmic_spectra(spec, times, freq)
    >>> my_spec.plot()

    """
    def __init__(self, data, times, freq):
        self.data = data
        self.times = times
        self.freq = freq

    def _update_data(self, data, times=None, freq=None):
        new_ds = copy(self)
        new_ds.data = data
        if times is not None:
            new_ds.times = times 
        if freq is not None: 
            new_ds.freq = freq
        return new_ds

    @u.quantity_input
    def background_sub1(self, percentile : u.percent = 1*u.percent):
        """
        Function to do a background subtraction and return a new dyanamic
        spectra object with the background subtracted data. 

        This function finds the background by dividing the data by the 
        average spectra of times when the standard dev is in bottom percentile
        defined by the parameter inputs. 

        Parameters
        ----------
        percentile : `~astropy.quantity.Quantity`
            the percentile of the standard dev for which data must be below.
        
        Notes
        -----
        Takes the log of the data before performing background subtraction. 
        """
        data = np.log10(self.data)
        data[np.isneginf(data)] = 0
        data_std = np.std(data, axis=0)
        data_std = data_std[np.nonzero(data_std)]
        min_std_indices = np.where(data_std < np.percentile(data_std, percentile.to_value('%')))[0]
        min_std_spec = data[:, min_std_indices]
        min_std_spec = np.mean(min_std_spec, axis=1)
        data = np.transpose(np.divide(np.transpose(data), min_std_spec))

        return self._update_data(data)

    def background_sub2(self):
        """
        Function to do a background subtraction and return a new dyanamic
        spectra object with the background subtracted data. 

        This function just divides the data in each frequency channel by the mean
        of the respective channel.

        Notes
        -----
        Takes the log of the data before performing background subtraction. 
        """
        data = np.log10(self.data)
        data[np.isneginf(data)] = 0

        for sb in np.arange(data.shape[0]):
              data[sb, :] = data[sb, :]/np.mean(data[sb, :])

        return self._update_data(data)

    def plot(self, axes=None, **kwargs):
        """
        Plot the dyanamic spectrum.

        Parameters
        ----------
        **kwargs : `~dict`
            additional keyword arguments for plt.imshow.

        """
        if axes is None:
            ax = plt.gca()

        im = ax.imshow(self.data, 
                  vmin=np.percentile(self.data, 1.5), 
                  vmax=np.percentile(self.data, 99.5), 
                  aspect="auto",
                  origin="lower",
                  extent=[dates.date2num(self.times[0]), dates.date2num(self.times[-1]),
                          self.freq[0].to_value(), self.freq[-1].to_value()], 
                  **kwargs)
        ax.invert_yaxis()
        ax.set_xlabel("Time ({:s} UT)".format(self.times[0].strftime("%Y-%m-%d")))
        ax.set_ylabel("Frequency ({:s})".format(self.freq.unit.to_string()))
        ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))


        # for i in plt.get_fignums():
        #     if ax in plt.figure(i).axes:
        #         plt.sca(ax)

        return im

    def crop_time(self, tstart, tend):
        """
        Function to return a new dyanamic spectrum only consisting of data
        between the given tstart and tend times.

        Parameters
        ----------
        tstart : `~datetime.datetime`, `~str`
            start time of timerange to truncate to.
        tend : `~datetime.datetime`, `~str`
            end time of timerange to truncate to.

        Returns
        -------
        `~dyanmic_spectra()`
            a new dyanmic spectrum object of data between given times.
        """

        if isinstance(tstart, str):
            tstart = parse_time(tstart).datetime
        if isinstance(tend, str):
            tend = parse_time(tend).datetime

        indices = (self.times>=tstart) & (self.times<=tend)

        truncated_data = self.data[:, indices]

        truncated_times = self.times[indices]

        return self._update_data(truncated_data, times=truncated_times)

    @u.quantity_input
    def crop_freq(self, freq_start : u.Hz, freq_end : u.Hz):
        """
        Function to return a new dyanamic spectrum only consisting of data
        between the given tstart and tend times.

        Parameters
        ----------
        freq_start : `~astropy.quantity.Quantity`
            freq min to crop from.
        freq_end : `~astropy.quantity.Quantity`
            freq max to crop from.

        Returns
        -------
        `~dyanmic_spectra()`
            a new dyanmic spectrum object of data cropped between given frequency range.
        """

        freq_start = freq_start.to_value(self.freq.unit)
        freq_end = freq_end.to_value(self.freq.unit)

        indices = (self.freq.value>=freq_start) & (self.freq.value<=freq_end)

        cropped_data = self.data[indices, :]
        cropped_freq = self.freq[indices]

        return self._update_data(cropped_data, freq=cropped_freq)

