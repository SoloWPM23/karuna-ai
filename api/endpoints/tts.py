# api/endpoints/tts.py
# Text-to-Speech endpoint

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import Optional
import base64
import logging

from api.models.request_models import TTSRequest, TTSResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Voice dan mood yang valid
VALID_VOICES = ["sarah", "charlotte", "aria", "roger", "jessica", "brian", "gavrila", "honeypie"]
VALID_MOODS = ["calm", "warm", "gentle", "concerned"]


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Konversi teks ke audio menggunakan Eleven Labs TTS.

    Menghasilkan audio berkualitas tinggi dengan suara natural
    yang support bahasa Indonesia.
    """
    try:
        from voice.tts_engine import TTSEngine, apply_mood

        # Validasi voice
        if request.voice and request.voice not in VALID_VOICES:
            raise HTTPException(
                status_code=400,
                detail=f"Voice tidak valid. Pilihan: {VALID_VOICES}"
            )

        # Buat engine
        engine = TTSEngine()

        # Set voice
        if request.voice:
            engine.set_voice_by_name(request.voice)

        # Terapkan mood jika ada
        if request.mood:
            if request.mood not in VALID_MOODS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Mood tidak valid. Pilihan: {VALID_MOODS}"
                )
            apply_mood(engine, request.mood)

        # Terapkan parameter kustom (after mood, so they override)
        if request.speed:
            engine.set_speed(request.speed)
        if request.stability is not None:
            engine.set_stability(request.stability)
        if request.similarity_boost is not None:
            engine.set_similarity_boost(request.similarity_boost)
        if request.style is not None:
            engine.set_style(request.style)

        # Generate audio
        audio_bytes = engine.synthesize(request.text)

        # Encode ke base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return TTSResponse(
            audio=audio_b64,
            format="mp3"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /tts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/file")
async def text_to_speech_file(
    text: str,
    voice: str = "sarah",
    mood: Optional[str] = None
):
    """
    Konversi teks ke file audio (return file langsung).

    Berguna untuk debugging atau jika client prefer menerima file.
    """
    import tempfile
    import os
    from voice.tts_engine import TTSEngine, apply_mood

    engine = TTSEngine()
    engine.set_voice_by_name(voice)

    if mood:
        apply_mood(engine, mood)

    # Simpan ke temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()

    try:
        engine.save(text, tmp.name)

        with open(tmp.name, "rb") as f:
            audio_data = f.read()

        os.unlink(tmp.name)

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=karuna_response.mp3"
            }
        )
    except Exception as e:
        # Cleanup temp file jika terjadi error
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        logger.error(f"Error in /tts/file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
