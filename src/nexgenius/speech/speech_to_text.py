from pathlib import Path
from typing import Union
import speech_recognition as sr

from src.nexgenius.parsers import AudioParser, YAMLParser

class SpeechRecognizerClient(AudioParser, YAMLParser):
    def __init__(self, conf_fname: str=None, conf_dir: Union[str, Path]=None) -> None:
        # Defaults
        if conf_fname is None:
            conf_fname = Path(__file__).stem
        
        if conf_dir is None:
            conf_dir = Path(__file__).parents[3] / "conf/speech"

        YAMLParser.__init__(self, conf_fname=f"{conf_fname}.yml", conf_dir=conf_dir)

        # Mapping dictionary to map Speech Recognizer services
        self.sr_engine_map = {
            'assemblyai': 'recognize_assemblyai',
            'aws': 'recognize_lex',
            'azure': 'recognize_azure',
            'gcp': 'recognize_google',
            'houndify': 'recognize_houndify',
            'ibm': 'recognize_ibm',
            'openai': 'recognize_whisper',
            'sphinx': 'recognize_sphinx',
            # 'tensorflow': 'recognize_tensorflow',
            'vosk': 'recognize_vosk',
            'wit': 'recognize_wit'
        }

    def transcribe(self, engine: str, audio_data: Union[Path, bytes, str], **engine_kwargs):
        engine = engine.strip().lower()
        if engine in self.sr_engine_map:
            return self.transcribe_sr(engine, audio_data, **engine_kwargs)
        elif engine == 'aws':
            return self.transcribe_aws(audio_data, **engine_kwargs)
        elif engine == 'azure':
            return self.transcribe_azure(audio_data, **engine_kwargs)
        elif engine == 'gcp':
            return self.transcribe_gcp(audio_data, **engine_kwargs)
        elif engine == 'transformers':
            return self.transcribe_transformers(audio_data, **engine_kwargs)
        else:
            available_engines = ", ".join(self.sr_engine_map.keys())
            raise ValueError(f"Engine '{engine}' not found.\nAvailable engines: {available_engines}")
    
    def transcribe_sr(self, engine: str, audio_data: Union[Path, bytes, str], **engine_kwargs):
        recognizer = sr.Recognizer()
        engine = engine.strip().lower()
        transcribe_method = getattr(recognizer, self.sr_engine_map[engine])
        audio_data, _ = self.get_sr_audio_data(audio_data, recognizer)

        try:
            return transcribe_method(audio_data, **engine_kwargs)
        except sr.UnknownValueError:
            return f"{engine.title()} couldn't understand audio"
        except sr.RequestError as err:
            return f"{engine.title()} service failed: {err}"

    def transcribe_transformers(self, audio_data: Union[Path, bytes, str], **engine_kwargs) -> str:
        from transformers import pipeline
        speech_pipeline = pipeline("automatic-speech-recognition")
        return speech_pipeline(audio_data, **engine_kwargs)["text"]
        
if __name__ == "__main__":
    speech2txt_obj = SpeechRecognizerClient()
    audio_fpath = ""  # TODO Update your audio file path
    openai_transcribed_txt = speech2txt_obj.transcribe("openai", audio_fpath)