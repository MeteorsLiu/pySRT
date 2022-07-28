"""
Defines autosub's main functionality.
"""

#!/usr/bin/env python

from __future__ import absolute_import, print_function, unicode_literals


import os
from json import JSONDecodeError
import subprocess
import tempfile

import json
import requests
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from autosub.constants import (
    LANGUAGE_CODES, GOOGLE_SPEECH_API_KEY, GOOGLE_SPEECH_API_URL,
)

DEFAULT_SUBTITLE_FORMAT = 'srt'
DEFAULT_CONCURRENCY = 10
DEFAULT_SRC_LANGUAGE = 'en'
DEFAULT_DST_LANGUAGE = 'en'



class FLACConverter(object): # pylint: disable=too-few-public-methods
    """
    Class for converting a region of an input audio or video file into a FLAC audio file
    """
    def __init__(self, source_path, include_before=0.25, include_after=0.25):
        self.source_path = source_path
        self.include_before = include_before
        self.include_after = include_after

    def __call__(self, region):
        try:
            start, end = region
            start = max(0, start - self.include_before)
            end += self.include_after
            #delete=False necessary for running on Windows
            temp = tempfile.NamedTemporaryFile(suffix='.flac', delete=False)
            program_ffmpeg = which("ffmpeg")
            command = [str(program_ffmpeg), "-ss", str(start), "-t", str(end - start),
                       "-y", "-i", self.source_path,
                       "-loglevel", "error", temp.name]
            use_shell = True if os.name == "nt" else False
            subprocess.check_output(command, stdin=open(os.devnull), shell=use_shell)
            read_data = temp.read()
            temp.close()
            os.unlink(temp.name)
            return read_data

        except KeyboardInterrupt:
            return None


class SpeechRecognizer(object): # pylint: disable=too-few-public-methods
    """
    Class for performing speech-to-text for an input FLAC file.
    """
    def __init__(self, language="ja", rate=16000, retries=3, api_key=GOOGLE_SPEECH_API_KEY):
        self.language = language
        self.rate = rate
        self.api_key = api_key
        self.retries = retries

    def __call__(self, data):
        try:
            for _ in range(self.retries):
                url = GOOGLE_SPEECH_API_URL.format(lang=self.language, key=self.api_key)
                headers = {"Content-Type": "audio/l16; rate=16000"}

                try:
                    resp = requests.post(url, data=data, headers=headers)
                except requests.exceptions.ConnectionError:
                    continue

                for line in resp.content.decode('utf-8').split("\n"):
                    try:
                        line = json.loads(line)
                        line = line['result'][0]['alternative'][0]['transcript']
                        return line[:1].upper() + line[1:]
                    except IndexError:
                        # no result
                        continue
                    except JSONDecodeError:
                        continue

        except KeyboardInterrupt:
            return None




def which(program):
    """
    Return the path for a given executable.
    """
    def is_exe(file_path):
        """
        Checks whether a file is executable.
        """
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)
    #necessary to run on Windows
    if os.name == "nt":
        program += ".exe"
    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        #looks for file in the script execution folder before checking on system path
        current_dir = os.getcwd()
        local_program = os.path.join(current_dir, program)
        if is_exe(local_program):
            return local_program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
    return None


def extract_audio(filename, channels=1, rate=16000):
    """
    Extract audio from an input file to a temporary WAV file.
    """
    temp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    if not os.path.isfile(filename):
        print("The given file does not exist: {}".format(filename))
        raise Exception("Invalid filepath: {}".format(filename))
    program_ffmpeg = which("ffmpeg")
    if not program_ffmpeg:
        print("ffmpeg: Executable not found on machine.")
        raise Exception("Dependency not found: ffmpeg")
    command = [str(program_ffmpeg), "-y", "-i", filename,
               "-ac", str(channels), "-ar", str(rate),
               "-loglevel", "error", temp.name]
    use_shell = True if os.name == "nt" else False
    subprocess.check_output(command, stdin=open(os.devnull), shell=use_shell)
    return temp.name, rate


