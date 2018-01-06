import scipy.io.wavfile as wav
import matplotlib.mlab as mlab
import numpy as np
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)

# Minimum amp to detect as peak
MIN_AMP = 10

# Diameter of check window for a value to be considered a peak
PEAK_NEIGHBORHOOD = 20

# FFT the signal and extract frequency components
WSIZE = 4096  # Window size for FFT
WRATIO = 0.9  # Overlap ration fo FFT


class AudioSample:
    def __init__(self, audio_path, start_time=0, end_time=None):

        samplerate, samples = wav.read(audio_path)
        self.samplerate = samplerate

        fs = samplerate
        start = fs * start_time
        end = len(samples) if end_time is None else fs * end_time

        self.samples = samples[start:end]  # Cut song

        self.peaks = None  # Found peaks
        self.spectrum = None  # Spectrum variable
        self.times = None  # Times corresponding to keys
        self.freqs = None  # Frequencies corresponding to keys


    def get_spectrum(self):
        print("Creating spectrogram")
        # Use matlab to generate spectrogram
        spectrum, freqs, t = mlab.specgram(self.samples, NFFT=WSIZE, Fs=self.samplerate,
                                           window=mlab.window_hanning, noverlap=int(WSIZE * WRATIO))

        spectrum = 10 * np.log10(spectrum)  # convert values do dB
        spectrum[spectrum == -np.inf] = 0  # replace infs with zeros

        return spectrum, freqs, t

    def get_peaks(self):
        if self.spectrum is None:
            spectrum, freqs, t = self.get_spectrum()
            self.spectrum = spectrum
            self.freqs = freqs
            self.times = t

        print("Finding peaks")
        self.peaks = self.get_2D_peaks(arr2D=self.spectrum, amp_min=MIN_AMP)
        print("Found %d peaks" % len(self.peaks[0]))

        return self.peaks, self.spectrum, self.times, self.freqs

    # Peak finding function from
    # https://github.com/worldveil/dejavu/blob/master/dejavu/decoder.py
    def get_2D_peaks(self, arr2D, amp_min=MIN_AMP):
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
