from webvad import getSlices
from autosub import SpeechRecognizer

from multiprocessing import Pool, TimeoutError


if __name__ == '__main__':
    recognizer = SpeechRecognizer()
    regions, voiced = getSlices("GVRD-94/1.wav")
    with Pool() as pool:
        for i in pool.imap(recognizer, voiced):
            print(i)
