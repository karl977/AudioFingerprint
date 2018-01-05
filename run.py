import scipy
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import scipy.io.wavfile as wav
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)



MIN_AMP = 10
PEAK_NEIGHBORHOOD = 20

# Peak finding function from
# https://github.com/worldveil/dejavu/blob/master/dejavu/decoder.py
def get_2D_peaks(arr2D, amp_min=MIN_AMP):

    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD)

    # find local maxima using our filter shape
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # Boolean mask of arr2D with True at peaks
    detected_peaks = local_max - eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    return frequency_idx, time_idx



def test():
    audiopath = "wav/all_my_life.wav"

    samplerate, samples = wav.read(audiopath)

    # FFT the signal and extract frequency components
    wsize = 4096
    wratio = 0.9

    fs = samplerate
    # First 20 seconds
    ed = fs * 20
    samples = samples[:ed]

    print("Creating spectragram")
    spectrum, freqs, t = mlab.specgram(samples, NFFT=wsize, Fs=fs, window=mlab.window_hanning, noverlap=int(wsize * wratio))

    # convert values do decibel
    spectrum = 10 * np.log10(spectrum)
    spectrum[spectrum == -np.inf] = 0  # replace infs with zeros

    print(t[100:110])

    peaks = get_2D_peaks(arr2D=spectrum, amp_min=5)
    print("Found %d peaks" % len(peaks[0]))

    plt.figure(figsize=(15, 7.5))
    plt.imshow(spectrum, origin="lower", aspect="auto", cmap="jet", interpolation="none")

    xlocs = np.arange(0, len(t), 200)
    plt.xticks(xlocs, ["%.02f" % t[l] for l in xlocs])
    ylocs = np.arange(0, len(freqs), 100)
    plt.yticks(ylocs, ["%.02f" % freqs[i] for i in ylocs])

    plt.plot(peaks[1], peaks[0], "ro")
    plt.colorbar()
    plt.show()

test()