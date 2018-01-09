from AudioSample import AudioSample
import matplotlib.pyplot as plt
import numpy as np
from Database import DbHelper

db = DbHelper()

"""
Plot the spectrogram and the peaks of a song using matplotlib
"""
def plot(audiopath = "wav/all_my_life.wav", start=28, end=38):
    audio_sample = AudioSample(audiopath, start, end)

    data = audio_sample.get_peaks()
    peaks = data[0]
    spectrum = data[1]
    t = data[2]
    freqs = data[3]

    plt.figure(figsize=(30, 15))
    plt.imshow(spectrum, origin="lower", aspect="auto", cmap="jet", interpolation="none")

    xlocs = np.arange(0, len(t), 200)
    plt.xticks(xlocs, ["%.02f" % t[l] for l in xlocs])
    ylocs = np.arange(0, len(freqs), 100)
    plt.yticks(ylocs, ["%.02f" % freqs[i] for i in ylocs])

    plt.ylabel("Frequency(Hz)")
    plt.xlabel("Time(s)")
    plt.plot(peaks[1], peaks[0], "ro")
    plt.colorbar().set_label("Signal strength(dB)")
    plt.show()


def plot_matches(song_id, hashes):
    """
    Plot the matches over time
    """
    x, y = [], []
    for row in hashes:
        hash_val, hash_time = row[0], row[1]
        for song_time in db.get_anc_hash_times(hash_val, song_id):
            x.append(song_time)
            y.append(hash_time)
    x = np.asarray(x) / 1000
    y = np.asarray(y) / 1000

    plt.scatter(x, y)
    plt.ylabel("Sample time(s)")
    plt.xlabel("Song time(s)")
    plt.xlim(5, 25)
    plt.show()