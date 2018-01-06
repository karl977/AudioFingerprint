import matplotlib.pyplot as plt
import numpy as np
from AudioSample import AudioSample
from Database import DbHelper
import AudioReader

import FingerPrint

db = DbHelper()

def test():
    audiopath = "wav/all_my_life.wav"
    song_name = "all_my_life.wav"
    song_id = db.get_song_id(song_name)


    audio_sample = AudioSample(audiopath, 0, 10)

    data = audio_sample.get_peaks()
    peaks = data[0]
    spectrum = data[1]
    t = data[2]
    freqs = data[3]

    print("Found %d peaks" % len(peaks[0]))

    # Save peak hashes to database
    # hash_generator = FingerPrint.hash_sequential(peaks, spectrum, t, freqs)
    # tot = 0
    # for data in hash_generator:
    #     hsh, time = FingerPrint.get_hashstr_sequential(data[0], data[1])
    #     db.insert_seq_hash(song_id, hsh, time)
    #     tot += 1
    # print("Total hashes saved %d" % tot)

    #return

    plt.figure(figsize=(15, 7.5))
    plt.imshow(spectrum, origin="lower", aspect="auto", cmap="jet", interpolation="none")

    xlocs = np.arange(0, len(t), 200)
    plt.xticks(xlocs, ["%.02f" % t[l] for l in xlocs])
    ylocs = np.arange(0, len(freqs), 100)
    plt.yticks(ylocs, ["%.02f" % freqs[i] for i in ylocs])

    plt.plot(peaks[1], peaks[0], "ro")
    plt.colorbar()
    plt.show()

#test()
#exit(0)

def process_all_songs_seq():
    paths, names = AudioReader.wav_paths()
    ids = []
    db.drop_tables()  # Delete previous data
    db.create_tables()
    for i in range(len(names)):
        ids.append(db.insert_song(names[i]))

    for i in range(len(paths)):
        save_fingerprints_to_DB_seq(paths[i], names[i], ids[i])


def save_fingerprints_to_DB_seq(path, song_name, song_id):
    print("\nProcessing %s" % song_name)

    audio_sample = AudioSample(path, 0, 100)
    peaks, spectrum, t, freqs = audio_sample.get_peaks()

    # Save peak hashes to database
    hash_generator = FingerPrint.hash_sequential(peaks, spectrum, t, freqs)
    tot = 0
    for data in hash_generator:
        hsh, time = FingerPrint.get_hashstr_sequential(data[0], data[1])
        db.insert_seq_hash(song_id, hsh, time)
        tot += 1
    print("%d hashes saved for %s" % (tot, song_name))





def count_matches():
    audiopath = "wav/all_my_life.wav"
    song_name = "all_my_life.wav"
    song_id = db.get_song_id(song_name)

    audio_sample = AudioSample(audiopath, 0, 10)
    peaks, spectrum, t, freqs = audio_sample.get_peaks()

    hash_generator = FingerPrint.hash_sequential(peaks, spectrum, t, freqs)
    print(spectrum.shape)
    print(t[0:10])
    tot = 0
    for data in hash_generator:
        hsh, time = FingerPrint.get_hashstr_sequential(data[0], data[1])
        tot += db.get_seq_hash_count(hsh)
    print("All hash matches %d" % tot)

    for data in hash_generator:
        hsh, time = FingerPrint.get_hashstr_sequential(data[0], data[1])
        tot += db.get_seq_hash_count_by_song(hsh, song_id)
    print("Correct song hash matches %d" % tot)

#process_all_songs()
#count_matches()

def process_all_songs_win():
    paths, names = AudioReader.wav_paths()
    ids = []
    db.drop_tables()  # Delete previous data
    db.create_tables()
    for i in range(len(names)):
        ids.append(db.insert_song(names[i]))

    for i in range(len(paths)):
        save_fingerprints_to_DB_win(paths[i], names[i], ids[i])


def save_fingerprints_to_DB_win(path, song_name, song_id):
    print("\nProcessing %s" % song_name)

    audio_sample = AudioSample(path, 0, 100)
    spectrum, t, freqs = audio_sample.get_spectrum()

    # Save peak hashes to database
    hash_generator = FingerPrint.hash_window(spectrum, t, freqs)
    tot = 0
    for data in hash_generator:
        hsh, time = FingerPrint.get_hashstr_window(data[0], data[1], data[2], data[3])
        db.insert_win_hash(song_id, hsh, time)
        tot += 1
    print("%d hashes saved for %s" % (tot, song_name))



def count_win_matches():
    audiopath = "wav/all_my_life.wav"
    song_name = "all_my_life.wav"
    song_id = db.get_song_id(song_name)

    audio_sample = AudioSample(audiopath, 10, 20)
    spectrum, t, freqs = audio_sample.get_spectrum()

    hash_generator = FingerPrint.hash_window(spectrum, t, freqs)

    tot = 0
    for data in hash_generator:
        hsh, time = FingerPrint.get_hashstr_window(data[0], data[1], data[2], data[3])
        count = db.get_win_hash_count(hsh)
        if count > 1: print("Duplicate")
        tot += count
    print("All hash matches %d" % tot)

    for data in hash_generator:
        hsh, time = FingerPrint.get_hashstr_window(data[0], data[1], data[2], data[3])
        tot += db.get_win_hash_count_by_song(hsh, song_id)
    print("Correct song hash matches %d" % tot)

process_all_songs_win()
count_win_matches()