# api/endpoints/emotion.py
# Emotion detection endpoint

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from api.models.request_models import EmotionRequest, EmotionResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Lazy loaded engine
_emotion_engine = None


def get_emotion_engine():
    """Ambil atau buat emotion engine."""
    global _emotion_engine
    if _emotion_engine is None:
        from s2_emotion.emotion_engine import EmotionEngine
        _emotion_engine = EmotionEngine("models/emotion_engine/final")
    return _emotion_engine


@router.post("/emotion", response_model=EmotionResponse)
async def analyze_emotion(request: EmotionRequest):
    """
    Deteksi emosi dari teks.

    Menggunakan S2: Emotion Engine (IndoBERT-based model)
    """
    try:
        engine = get_emotion_engine()
        result = engine.analyze(request.text)

        return EmotionResponse(
            dominant=result.dominant,
            score=result.score,
            distribution=result.distribution,
            topics=result.topics if request.return_topics else None,
            distress_score=result.distress_score
        )

    except Exception as e:
        logger.error(f"Error in /emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emotion/labels")
async def get_emotion_labels():
    """Daftar label emosi yang tersedia."""
    return {
        "emotions": ["senang", "sedih", "marah", "takut", "kaget", "jijik", "netral"],
        "topics": ["pekerjaan", "relationship", "keluarga", "kesehatan", "finansial", "self", "other"]
    }
