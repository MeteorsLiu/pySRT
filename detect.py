
from fileinput import filename
from autosub import find_speech_regions
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

from pySRT.autosub import FLACConverter
async def getGoogle(data):
    timeout = aiohttp.ClientTimeout(total=300)
    headers = {
        "Content-Type": "audio/l16; rate=44100;",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession(headers=headers) as session:   
        for t in range(5):
            try:
                async with session.post(GOOGLE_SPEECH_API_URL.format(lang="ja", key=GOOGLE_SPEECH_API_KEY), data=data) as resp:
                    res = await resp.text()
                    for line in res.split("\n"):
                        line = json.loads(line)
                        print(line)
                        line = line['result'][0]['alternative'][0]['transcript']
                        return line[:1].upper() + line[1:]
            except IndexError:
                return None
            except Exception as e:
                time.sleep(1)
                print("Retry %d" % t)
                print(e)
async def main():
    regions, filename = find_speech_regions("../GVRD-94/GVRD-94_01.mkv")
    trans = []
    converter = FLACConverter(source_path=filename)
    with Pool(10) as pool:
        for i in pool.imap(converter, regions):
            t = await getGoogle(i)
            if t:
                print(t)
                trans.append(t)
    timed = [(r, t) for r, t in zip(regions, trans) if t]
    formatter = FORMATTERS.get("srt")
    formatted_subtitles = formatter(timed)
    with open("../GVRD-94/GVRD-94_01.srt", 'wb') as output_file:
        output_file.write(formatted_subtitles.encode("utf-8"))
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())