import matplotlib.pyplot as plt
import numpy as np
from AudioSample import AudioSample
from Database import DbHelper
import AudioReader
import PlotSample
import FingerPrint

db = DbHelper()


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

#process_all_songs_win()
#count_win_matches()

def process_all_songs_anchor():
    paths, names = AudioReader.wav_paths()
    ids = []
    db.drop_tables()  # Delete previous data
    db.create_tables()
    for i in range(len(names)):
        ids.append(db.insert_song(names[i]))

    for i in range(len(paths)):
        save_fingerprints_to_DB_anchor(paths[i], names[i], ids[i])

    duplicates = db.count_anc_duplicate_hashes()
    print("%d total duplicate hash values" % duplicates)

def save_fingerprints_to_DB_anchor(path, song_name, song_id):
    print("\nProcessing %s" % song_name)
    # Fingerprints only first 3 minutes of a song due to high memory usage
    audio_sample = AudioSample(path, 0, 60)
    peaks, spectrum, t, freqs = audio_sample.get_peaks()

    # Save peak hashes to database
    hashes = FingerPrint.hash_anchor(peaks, spectrum, t, freqs)
    db.insert_anc_bulk(song_id, hashes)

    print("%d hashes saved for %s" % (len(hashes), song_name))

import operator

def count_anchor_matches():
    #audiopath = "wav/rec/all_my_life_0.10-0.20.wav"
    audiopath = "wav/rec/ring_of_fire_0.10-0.20.wav"
    song_name = "all_my_life.wav"
    song_id = db.get_song_id(song_name)

    audio_sample = AudioSample(audiopath)
    peaks, spectrum, t, freqs = audio_sample.get_peaks()

    hashes = FingerPrint.hash_anchor(peaks, spectrum, t, freqs)
    print("Created %d hashes from sample" % len(hashes))

    song_counts = {}
    for row in hashes:
        hsh, time = row[0], row[1]
        counts = db.get_song_match_count(hsh)
        for song_row in counts:
            s_id, count = song_row[0], song_row[1]
            if s_id not in song_counts:
                song_counts[s_id] = count
            else:
                song_counts[s_id] += count

    sorted_counts = sorted(song_counts.items(), key=operator.itemgetter(1))
    sorted_counts.reverse()
    for song_count in sorted_counts:
        s_id, count = song_count[0], song_count[1]
        song_name = db.get_song_name(s_id)
        print("%d matches in %s" % (count, song_name))

    return sorted_counts[0][0], audio_sample, hashes  # Return song with highest amount of matches




#process_all_songs_anchor()
song_id, sample, hashes = count_anchor_matches()
PlotSample.plot_matches(song_id, hashes)

#all = db.count_anc_hashes()
#duplicates = db.count_anc_duplicate_hashes()
#print("%d duplicates from total %d hash values" % (duplicates, all))