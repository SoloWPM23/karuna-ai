# api/endpoints/models_info.py
# Model information endpoint

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models/info")
async def get_models_info():
    """
    Informasi tentang model yang digunakan.
    """
    import torch

    return {
        "models": {
            "emotion_engine": {
                "name": "IndoBERT-based Emotion Classifier",
                "path": "models/emotion_engine/final",
                "device": "cuda" if torch.cuda.is_available() else "cpu",
                "classes": ["senang", "sedih", "marah", "takut", "kaget", "jijik", "netral"]
            },
            "crisis_detector": {
                "name": "Crisis Detection System (3-layer)",
                "path": "models/crisis_detector/final",
                "layers": {
                    "layer1": "Keyword/Regex",
                    "layer2": "IndoBERT classifier",
                    "layer3": "History trend analysis"
                },
                "levels": ["NORMAL", "L1", "L2", "L3"]
            }
        },
        "llm": {
            "provider": "Groq",
            "model": "llama-3.3-70b-versatile"
        },
        "voice": {
            "stt": "Eleven Labs Scribe",
            "tts": "Eleven Labs Multilingual v3"
        }
    }


@router.get("/models/loaded")
async def get_loaded_models():
    """Cek model mana yang sudah loaded."""
    return {
        "status": "ready",
        "loaded": [
            "emotion_engine",
            "crisis_detector_base"
        ]
    }
