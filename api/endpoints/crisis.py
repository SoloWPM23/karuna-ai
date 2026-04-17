# api/endpoints/crisis.py
# Crisis detection endpoint

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass
import logging

from api.models.request_models import CrisisRequest, CrisisResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/crisis", response_model=CrisisResponse)
async def analyze_crisis_endpoint(request: CrisisRequest):
    """
    Deteksi level krisis dari teks dan riwayat emosi.

    Menggunakan S3: Crisis Detection System (3-layer)
    - Layer 1: Keyword/Regex detection
    - Layer 2: IndoBERT model
    - Layer 3: History trend analysis
    """
    try:
        from s3_crisis.cds_engine import analyze_crisis

        # Konversi emotion_history jika disediakan
        emotion_objs = []
        if request.emotion_history:
            @dataclass
            class EmotionObj:
                distress_score: float

            emotion_objs = [
                EmotionObj(e.get("distress_score", 0.0))
                for e in request.emotion_history
            ]

        result = analyze_crisis(request.text, emotion_objs)

        return CrisisResponse(
            level=result.level,
            score=result.score,
            triggers=result.triggers,
            detail=result.detail
        )

    except Exception as e:
        logger.error(f"Error in /crisis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crisis/levels")
async def get_crisis_levels():
    """Penjelasan level krisis."""
    return {
        "levels": {
            "NORMAL": {
                "description": "Tidak ada sinyal krisis terdeteksi",
                "action": "Lanjutkan percakapan normal"
            },
            "L1": {
                "description": "Sedikit tanda-tanda distress",
                "action": "Perhatikan dan tunjukkan empati"
            },
            "L2": {
                "description": "Tanda-tanda krisis yang nyata",
                "action": "Berikan dukungan lebih, pertimbangkan referal"
            },
            "L3": {
                "description": "Krisis serius - risiko tinggi",
                "action": "Segera berikan nomor bantuan krisis (119 ext 8)"
            }
        }
    }
