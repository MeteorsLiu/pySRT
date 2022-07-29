
from autosub import find_speech_regions
import os
from multiprocessing import Pool, TimeoutError
from autosub.formatters import FORMATTERS

from autosub.constants import (
    LANGUAGE_CODES, GOOGLE_SPEECH_API_KEY, GOOGLE_SPEECH_API_URL,
)
import json
import time

from autosub import FLACConverter, SpeechRecognizer

def main():
    regions, filename = find_speech_regions("../GVRD-94/GVRD-94_01.mkv")
    trans = []
    converter = FLACConverter(source_path="../GVRD-94/GVRD-94_01.mkv")
    recongizer = SpeechRecognizer()
    with Pool(10) as pool:
        for i in pool.imap(converter, regions):
            t = recongizer(i)
            if t:
                print(t)
                trans.append(t)
    timed = [(r, t) for r, t in zip(regions, trans) if t]
    formatter = FORMATTERS.get("srt")
    formatted_subtitles = formatter(timed)
    with open("../GVRD-94/GVRD-94_01.srt", 'wb') as output_file:
        output_file.write(formatted_subtitles.encode("utf-8"))
if __name__ == '__main__':
    main()