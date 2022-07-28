from webvad import getSlices
from autosub import SpeechRecognizer
import os
from multiprocessing import Pool, TimeoutError
from autosub.formatters import FORMATTERS


if __name__ == '__main__':
    recognizer = SpeechRecognizer()
    regions, voiced = getSlices("../GVRD-94/1.wav")
    trans = []
    with Pool(os.cpu_count()+3) as pool:
        for i in pool.imap(recognizer, voiced):
            if not i is None:
                trans.append(i)
                print(i)

    timed = [(r, t) for r, t in zip(regions, trans) if t]
    formatter = FORMATTERS.get("srt")
    formatted_subtitles = formatter(timed)
    with open("../GVRD-94/GVRD-94_01.srt", 'wb') as output_file:
        output_file.write(formatted_subtitles.encode("utf-8"))