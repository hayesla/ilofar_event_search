import numpy as np 
from astropy import units
from sunpy.time import parse_time
from astropy import units as u 
from astropy.time import TimeDelta
from pathlib import Path

def read_bst_data(filename):
    """
    Function to read the BST .dat files and return the spectral array, 
    frequency array and time array.

    Parameters
    ----------
    filename : ~`str`
        path to file to be read

    Returns
    -------
    spec : ~`np.ndarray`
        2D array of dynamic spectra from file
    time : ~`np.ndarray`
        1D array of datetime objects corresponding to time of observation
    freq : ~`np.ndarray`
        1D array of the observing frequencies

    Notes
    -----
    Assuming mode 357! Also use with caution as I'm not 100% about
    everything yet.

    Examples
    --------
    >>> spec, time, data = read_bst_data("./bst_files/20170910_070804_bst_00X.dat")

    """
    filename = Path(filename) # here just in case path given
    
    f = open(filename, "rb")
    data_bytes = f.read()
    f.close()
    data_array = np.fromfile(filename)

    # get the bit mode - should be 8 for I-LOFAR
    bit_mode = len(data_bytes)/len(data_array)

    num_beamlets = int(244*16/bit_mode)

    # this part takes care of the data not being an integer multiple of the beamlets
    full_data_len = int(len(data_array)/num_beamlets)*num_beamlets
    if len(data_array)!=full_data_len:
        data_array = data_array[: -(len(data_array) - full_data_len)]

    spec = data_array.reshape(-1, num_beamlets).T

    # get corresponding frequency array - lba (low band antenna), hba (high band antenna)
    freq_lba = subband_to_freq(np.arange(54, 452+1, 2), 1) # the +1 here is to make sure 452 is incl in array.
    freq_hba1 = subband_to_freq(np.arange(54, 452+1, 2), 2) 
    freq_hba2 = subband_to_freq(np.arange(54, 228+1, 2), 3)
    # concatenate the frequency axis to one array
    freq_axis = np.concatenate((freq_lba, freq_hba1, freq_hba2))

    # get the time array 
    # the start time in filename and temporal resolution is 1 sec.
    time_array = (parse_time(filename.name[0:15]) + TimeDelta(np.arange(spec.shape[1]), format="sec")).datetime

    return spec, time_array, freq_axis




def subband_to_freq(sb, nyquist_zone):
    """
    The observational signal is divided into 512 frequency
    subbands, and the bandwidth is dicated by the sampling 
    clock. To get the frequency from the subband number need 
    equation below. 

    Parameters
    ----------
    sb : ~`int` 
        the subband number
    nyquist_zone : `~int`
        the int for the different modes (options 1, 2, 3)

    Returns
    -------
    freq : ~`astropy.units.quantity`
        the frequency of the subband

    Notes
    -----
    This is written and somewhat understood for mode 357.
    For mode 3 and 5 - there are 200 subbands each and then 
    88 subbands for mode 7. 

    What it should be is that:
        * Mode 3 - subbands = 54 to 452 (in steps of 2) and nyquist zone = 1
        * Mode 5 - subbands = 54 to 452 (in steps of 2) and nyquist zone = 3
        * Mode 7 - subbands = 54 to 228 (in steps of 2) and nyquist zone = 3
    """
    clock = 200*u.MHz 
    freq = (nyquist_zone - 1 + sb/512)*(clock/2)
    return freq 



