import subprocess
import os

MP3_FOLDER = 'mp3'
WAV_FOLDER = 'wav'

def mp3_paths():
    """
    Prints all files in mp3 folder
    :return: Tuple of full paths and names of mp3 files
    """
    paths, names = [], []
    for file in os.listdir(MP3_FOLDER):
        if file.endswith(".mp3"):
            paths.append(os.path.abspath(os.path.join(MP3_FOLDER, file)))
            names.append(file)
    return paths, names


def convert_mp3_to_wav():
    """
    Converts mp3 files to mono wav using SOX application
    """
    paths, names = mp3_paths()

    wav_folder = os.path.join(os.getcwd(), WAV_FOLDER)

    for i in range(len(names)):
        name = names[i].split(".")[-2] + ".wav"
        wav_path = os.path.join(wav_folder, name)

        if not os.path.isfile(wav_path):
            subprocess.call(['sox', '-v', '0.75', paths[i],
                             '-r', '48k', wav_path, 'remix', '1,2'])


convert_mp3_to_wav()