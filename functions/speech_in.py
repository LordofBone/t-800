import subprocess
from config.tensorflowasr import *


def listen():
    """
    Listen to the audio input and return the text
    :return:
    """
    subprocess.call([f'rec {audio_file} rate 32k silence 1 0.1 5% 1 1.0 5%'], shell=True)


if __name__ == '__main__':
    print(listen())
