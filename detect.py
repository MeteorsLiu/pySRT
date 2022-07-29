from webvad import getSlices
from autosub import SpeechRecognizer
import os
from multiprocessing import Pool, TimeoutError
from autosub.formatters import FORMATTERS
import aiohttp
import asyncio
from autosub.constants import (
    LANGUAGE_CODES, GOOGLE_SPEECH_API_KEY, GOOGLE_SPEECH_API_URL,
)
import json
import time
async def getGoogle(data):
    timeout = aiohttp.ClientTimeout(total=300)
    headers = {"Content-Type": "audio/l16; rate=16000;"}
    async with aiohttp.ClientSession() as session:   
        for t in range(5):
            try:
                async with session.post(GOOGLE_SPEECH_API_URL.format(lang="ja", key=GOOGLE_SPEECH_API_KEY), data=data, headers=headers, timeout=timeout) as resp:
                    res = await resp.text()
                    for line in res.split("\n"):
                        line = json.loads(line)
                        line = line['result'][0]['alternative'][0]['transcript']
                        return line[:1].upper() + line[1:]
            except Exception as e:
                time.sleep(1)
                print("Retry %d" % t)
                print(e)
async def main():
    regions, voiced = getSlices("../GVRD-94/1.wav")
    trans = []
    for v in voiced:
        i = await getGoogle(v)
        if i:
            print(i)
            trans.append(i)
    timed = [(r, t) for r, t in zip(regions, trans) if t]
    formatter = FORMATTERS.get("srt")
    formatted_subtitles = formatter(timed)
    with open("../GVRD-94/GVRD-94_01.srt", 'wb') as output_file:
        output_file.write(formatted_subtitles.encode("utf-8"))
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())