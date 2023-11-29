# Path: src/nexgenius/parsers/audio.py

import io
from pathlib import Path
from typing import Union

import speech_recognition as sr

class AudioParser:

    def __init__(self, audio_path: Union[str, Path], audio_type):
        self.audio_path = audio_path
        self.audio_type = audio_type

    def parse(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.file) as source:
            audio = r.record(source)
        return r.recognize_google(audio)

    def get_sr_audio_data(self, input_audio_data: Union[str, Path, bytes, bytearray], recognizer: sr.Recognizer = None):
        """Get audio data compatible with `speech_recognition` package

        Args:
            input_audio_data (Union[str, Path, bytes]): Input audio data
            recognizer (sr.Recognizer, optional): recognizer. Defaults to None.

        Returns:
            _type_: _description_
        """
        if isinstance(input_audio_data, (Path, str)):
            input_audio_data = str(input_audio_data)
        elif isinstance(input_audio_data, (bytes, bytearray)):
            input_audio_data = io.BytesIO(input_audio_data)
        else:
            raise TypeError("Invalid `input_audio_data` type, must be a pth or file-like object")
        
        if recognizer is None:
            recognizer = sr.Recognizer()

        with sr.AudioFile(input_audio_data) as source:
            audio_data = recognizer.record(source)

        return audio_data, recognizer