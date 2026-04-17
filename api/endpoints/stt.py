# api/endpoints/stt.py
# Speech-to-Text endpoint

from fastapi import APIRouter, HTTPException, UploadFile, File
import base64
import logging

from api.models.request_models import STTRequest, STTResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(request: STTRequest):
    """
    Konversi audio ke teks menggunakan Eleven Labs STT.

    Mendukung bahasa Indonesia dengan akurat.
    """
    try:
        from voice.stt_engine import transcribe_audio

        # Decode base64
        audio_bytes = base64.b64decode(request.audio)

        # Transkripsi
        text = transcribe_audio(audio_bytes, language=request.language or "id")

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Tidak dapat melakukan transkripsi audio"
            )

        return STTResponse(
            text=text,
            language=request.language or "id"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /stt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt/file")
async def speech_to_text_file(
    audio: UploadFile = File(...),
    language: str = "id"
):
    """
    Konversi file audio ke teks.

    Upload file audio langsung (bukan base64).
    """
    try:
        from voice.stt_engine import transcribe_file
        import tempfile
        import os

        # Baca uploaded file
        audio_bytes = await audio.read()

        # Simpan ke temp file
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            # Transkripsi
            text = transcribe_file(tmp_path, language)
        finally:
            os.unlink(tmp_path)

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Tidak dapat melakukan transkripsi audio"
            )

        return {"text": text, "language": language}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /stt/file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
