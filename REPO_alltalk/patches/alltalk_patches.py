"""Freedom System changes to stock AllTalk v2, applied in memory at load time.

Keys are paths relative to the AllTalk folder. Each entry is (find, replace); the
find text must appear exactly once in the stock file, or AllTalk is stopped with a
message naming the patch - an AllTalk update that rewrites the same code fails
loudly instead of silently running without these changes.

`_fa` inside replacements is the REPO_alltalk runtime layer (_boot/freedom_alltalk.py).
"""

_FA = "__import__('freedom_alltalk')"

PATCHES = {
    "tts_server.py": [
        (   # voice mode asks for voices by file name ("Freya.wav") on the OpenAI endpoint
            '''        supported_voices = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
        if value not in supported_voices:
            raise ValueError(f"Voice must be one of {supported_voices}")
        return value''',
            '''        supported_voices = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
        if value in supported_voices:
            return value
        if isinstance(value, str) and value.endswith(".wav"):
            if (this_dir / "voices" / value).exists():
                return value
        raise ValueError(f"Voice must be one of {supported_voices} or a .wav filename in the voices/ directory")''',
        ),
        (
            '''        mapped_voice = voice_mapping.get(voice)
        if not mapped_voice:
            print_message(f"Unsupported voice: {voice}", "error", "TTS")
            raise ValueError("Unsupported voice")''',
            '''        mapped_voice = voice_mapping.get(voice)
        if not mapped_voice:
            if isinstance(voice, str) and voice.endswith(".wav") and (this_dir / "voices" / voice).exists():
                mapped_voice = voice
                print_message(f"Using direct voice file: {voice}", "debug_openai", "TTS")
            else:
                print_message(f"Unsupported voice: {voice}", "error", "TTS")
                raise ValueError("Unsupported voice")''',
        ),
        (   # narrator combine() wrote to a hardcoded outputs/ instead of the output setting
            '''output_file_path = os.path.join(this_dir / "outputs" / filename)''',
            '''output_file_path = os.path.join(this_dir / config.get_output_directory() / filename)''',
        ),
    ],
    "config.py": [
        (   # default voice = first voice file found, not a hardcoded name
            '''from pydantic import BaseModel, ConfigDict, AliasGenerator, AliasChoices, Field
''',
            '''from pydantic import BaseModel, ConfigDict, AliasGenerator, AliasChoices, Field

def get_dynamic_default_voice():
    """Dynamically discover the first available voice file for defaults"""
    voices_dir = Path(__file__).parent / "voices"
    if not voices_dir.exists():
        return "female_01.wav"
    voice_files = sorted(voices_dir.glob("*.wav"))
    return voice_files[0].name if voice_files else "female_01.wav"

_FREEDOM_SETTINGS = ''' + _FA + '''.SETTINGS
''',
        ),
        (
            '''class AlltalkConfigRvcSettings(BaseModel):
''',
            '''class AlltalkConfigRvcSettings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
''',
        ),
        (
            '''    tgwui_narrator_voice: str = "female_01.wav"''',
            '''    tgwui_narrator_voice: str = Field(default_factory=get_dynamic_default_voice)''',
        ),
        (
            '''    tgwui_character_voice: str = "female_01.wav"''',
            '''    tgwui_character_voice: str = Field(default_factory=get_dynamic_default_voice)''',
        ),
        (   # settings files live in REPO_alltalk/settings, like ComfyUI's --base-directory
            '''os.path.join(__this_dir, "system", "tts_engines", "tts_engines.json")''',
            '''os.path.join(_FREEDOM_SETTINGS, "system", "tts_engines", "tts_engines.json")''',
        ),
        (
            '''    def __init__(self, config_path: Path | str = __this_dir / "confignew.json"):''',
            '''    def __init__(self, config_path: Path | str = Path(_FREEDOM_SETTINGS) / "confignew.json"):''',
        ),
        (
            '''        return AlltalkConfig.__this_dir / "confignew.json"''',
            '''        return Path(_FREEDOM_SETTINGS) / "confignew.json"''',
        ),
        (
            '''os.path.join(__this_dir, "mem_config.json")''',
            '''os.path.join(_FREEDOM_SETTINGS, "mem_config.json")''',
        ),
    ],
    "script.py": [
        (   # Voice2RVC scratch files -> the output folder setting (REPO_alltalk/outputs)
            '''input_tts_path = this_dir / "outputs" / "voice2rvcInput.wav"''',
            '''input_tts_path = this_dir / config.get_output_directory() / "voice2rvcInput.wav"''',
        ),
        (
            '''output_rvc_path = this_dir / "outputs" / "voice2rvcOutput.wav"''',
            '''output_rvc_path = this_dir / config.get_output_directory() / "voice2rvcOutput.wav"''',
        ),
        (   # Transcribe / Dictate tabs -> REPO_alltalk/transcriptions
            '''base_dir = os.path.join(setup_script_dir, "transcriptions")''',
            '''base_dir = ''' + _FA + '''.TRANSCRIPTIONS''',
        ),
        (
            '''uploads_dir = os.path.join(del_upload_script_dir, "transcriptions", "uploads")''',
            '''uploads_dir = os.path.join(''' + _FA + '''.TRANSCRIPTIONS, "uploads")''',
        ),
        (
            '''transcripts_dir = os.path.join(trans_script_dir, "transcriptions", "live_dictation")''',
            '''transcripts_dir = os.path.join(''' + _FA + '''.TRANSCRIPTIONS, "live_dictation")''',
        ),
    ],
    "system/tts_engines/xtts/model_engine.py": [
        (   # voices can be stock (app) or the user's (REPO_alltalk/voices)
            '''voice_set_path = os.path.join(self.main_dir, "voices", "xtts_multi_voice_sets", voice_set)''',
            '''voice_set_path = ''' + _FA + '''.voice_path("xtts_multi_voice_sets", voice_set)''',
        ),
        (
            '''normalized_path = os.path.normpath(os.path.join(self.main_dir, "voices", voice))''',
            '''normalized_path = os.path.normpath(''' + _FA + '''.voice_path(voice))''',
        ),
    ],
    "system/tts_engines/f5tts/model_engine.py": [
        (
            '''voice_dir = self.main_dir / "voices" / voice.rstrip('/')''',
            '''voice_dir = Path(''' + _FA + '''.voice_path(voice.rstrip('/')))''',
        ),
        (
            '''ref_audio_path = self.main_dir / "voices" / voice''',
            '''ref_audio_path = Path(''' + _FA + '''.voice_path(voice))''',
        ),
    ],
    "system/proxy_module/proxy_manager.py": [
        (   # proxy.log -> REPO_alltalk/logs
            '''self.logs_path = self.base_path / "logs"''',
            '''self.logs_path = Path(''' + _FA + '''.LOGS)''',
        ),
    ],
    "tts_mem.py": [
        (
            '''flask_app.config['OUTPUT_FOLDER'] = str(Path(os.getcwd()) / 'outputs')''',
            '''flask_app.config['OUTPUT_FOLDER'] = ''' + _FA + '''.OUTPUTS''',
        ),
    ],
    "diagnostics.py": [
        (
            '''log_file = 'diagnostics.log\'''',
            '''log_file = os.path.join(''' + _FA + '''.LOGS, 'diagnostics.log')''',
        ),
    ],
    "test_server.py": [
        (
            '''self.log_file = datetime.now().strftime('alltalk_test_%Y%m%d_%H%M%S.log')''',
            '''self.log_file = __import__('os').path.join(''' + _FA + '''.LOGS, datetime.now().strftime('alltalk_test_%Y%m%d_%H%M%S.log'))''',
        ),
    ],
}
