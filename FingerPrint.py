from Database import DbHelper
import hashlib
from numba import jit
import numpy as np

db = DbHelper()

FREQUENY_RANGES = (500,  1000, 1500, 2000, 2500, 3000, 3500 , 4000, 10000000)
TOT_RANGES = len(FREQUENY_RANGES)

@jit(nopython=True)
def get_range_idx(freq):
    i = 0
    while FREQUENY_RANGES[i] < freq:
        i += 1
    return i

def hash_sequential(peaks, spectrum, t, freq):
    """
    Take 2 sequential points within multiple
    ranges 0-1000, 1000-2000, 2000-3000, 3000-4000.

    Put together the frequencies and time differences of these points
    to produce a hash
    """
    peak_freq = np.around(freq[peaks[0]], -1)  # Round frequencies to nearest 10
    peak_times = np.around(t[peaks[1]] * 1000, -1)  # Round times to nearest 10 ms

    # Sort by ascending time
    sort_order = np.argsort(peak_times)
    peak_times = peak_times[sort_order]
    peak_freq = peak_freq[sort_order]

    freq_buffer = [[0]] * TOT_RANGES
    time_buffer = [[0]] * TOT_RANGES

    MIN_TIME_DELTA = 0

    for i in range(len(peak_freq)):
        freq = peak_freq[i]
        time = peak_times[i]

        range_idx = get_range_idx(freq)

        if range_idx < TOT_RANGES - 2:  # Frequency must be in range
            #if(time - time_buffer[range_idx][-1]) >= MIN_TIME_DELTA:  # Minimum time between
            freq_buffer[range_idx].append(freq)
            time_buffer[range_idx].append(time)
            if len(freq_buffer[range_idx]) > 4:
                yield freq_buffer[range_idx][-4:], time_buffer[range_idx][-4:]

HASHLEN = 20
def save_hash1(freq1, freq2, time1, time2):
    tp = (str(freq1), str(freq2), str(time2 - time1))
    hash_ob = hashlib.sha1(str("%s %s %s" % tp).encode('utf-8'))

    db.insert_seq_hash(hash_ob.digest()[:HASHLEN], time1)

def get_hash(freqs, times):
    """
    Calculates hash with four consecutive frequencies
    """
    time_difference = times[3] - times[0]

    tp = (str(freqs[0]), str(freqs[1]), str(freqs[2]), str(freqs[3]))
    hash_ob = hashlib.sha1(str("%s %s %s %s" % tp).encode('utf-8'))

    return hash_ob.digest()[:HASHLEN], times[0]


"""
Finds highest peaks in each time segment 
"""
TOP_FREQ = 0
def hash_window(peaks, spectrum, t, freq):
    peak_freq = np.around(freq[peaks[0]], -1)  # Round frequencies to nearest 10
    peak_times = np.around(t[peaks[1]] * 1000, -1)  # Round times to nearest 10 ms

    # Sort by ascending time
    sort_order = np.argsort(peak_times)
    peak_times = peak_times[sort_order]
    peak_freq = peak_freq[sort_order]

    pass

"""
Use time pairs of peaks and hash with
the frequencies and time differences between them
"""
def hash_anchors(peaks, spectrum, t, freq):
    pass
