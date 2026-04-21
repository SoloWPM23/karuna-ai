# voice/__init__.py
# Voice module untuk KarunaAI — STT & TTS

from importlib import import_module

__all__ = [
    # STT
    "AudioRecorder",
    "transcribe_audio",
    "transcribe_file",
    "record_and_transcribe",
    # TTS
    "TTSEngine",
    "get_engine",
    "speak",
    "speak_to_file",
    "apply_mood",
    "list_voices",
    "AVAILABLE_VOICES",
    "MOOD_PRESETS",
]


_STT_EXPORTS = {
    "AudioRecorder",
    "transcribe_audio",
    "transcribe_file",
    "record_and_transcribe",
}

_TTS_EXPORTS = {
    "TTSEngine",
    "get_engine",
    "speak",
    "speak_to_file",
    "apply_mood",
    "list_voices",
    "AVAILABLE_VOICES",
    "MOOD_PRESETS",
}


def __getattr__(name):
    if name in _STT_EXPORTS:
        module = import_module("voice.stt_engine")
        return getattr(module, name)
    if name in _TTS_EXPORTS:
        module = import_module("voice.tts_engine")
        return getattr(module, name)
    raise AttributeError(f"module 'voice' has no attribute '{name}'")
