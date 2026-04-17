# api/endpoints/voices.py
# Voices listing endpoint

from fastapi import APIRouter, HTTPException
import base64
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_voice_description(name: str) -> str:
    """Deskripsi untuk tiap voice."""
    descriptions = {
        "sarah": "Female, warm dan friendly - cocok untuk percakapan sehari-hari",
        "charlotte": "Female, calm dan professional",
        "aria": "Female, expressive dan animated",
        "roger": "Male, professional dan clear",
        "jessica": "Female, conversational",
        "brian": "Male, deep voice",
        "gavrila": "Female, young dan warm",
        "honeypie": "Female, sweet dan warm"
    }
    return descriptions.get(name, "Unknown voice")


@router.get("/voices")
async def list_voices():
    """
    Daftar suara TTS yang tersedia beserta mood preset.
    """
    from voice.tts_engine import AVAILABLE_VOICES, MOOD_PRESETS

    return {
        "voices": {
            name: {
                "voice_id": voice_id,
                "description": _get_voice_description(name)
            }
            for name, voice_id in AVAILABLE_VOICES.items()
        },
        "moods": MOOD_PRESETS
    }


@router.get("/voices/{voice_name}/preview")
async def voice_preview(voice_name: str, text: str = "Halo, aku Karuna."):
    """
    Preview audio untuk voice tertentu.

    Args:
        voice_name: Nama voice
        text: Teks untuk preview
    """
    from voice.tts_engine import TTSEngine, AVAILABLE_VOICES

    if voice_name not in AVAILABLE_VOICES:
        raise HTTPException(status_code=404, detail="Voice tidak ditemukan")

    engine = TTSEngine()
    engine.set_voice_by_name(voice_name)

    audio_bytes = engine.synthesize(text)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    return {
        "audio": audio_b64,
        "format": "mp3"
    }
