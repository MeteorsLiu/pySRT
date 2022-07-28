from webvad import getSlices
from autosub import SpeechRecognizer
import os
from multiprocessing import Pool, TimeoutError
from googletrans import Translator

if __name__ == '__main__':
    recognizer = SpeechRecognizer()
    regions, voiced = getSlices("GVRD-94/1.wav")
    trans = []
    with Pool(os.cpu_count()+3) as pool:
        for i in pool.imap(recognizer, voiced):
            if i:
                _trans = translator.translate(i, dest='zh-cn')
                trans.append(_trans)
                print(_trans)

    print([(r, t) for r, t in zip(regions, trans) if t])
