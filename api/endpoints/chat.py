# api/endpoints/chat.py
# Chat endpoint - Utama untuk percakapan dengan KarunaAI

from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid
import logging

from api.models.request_models import ChatRequest, ChatResponse
from pipeline.orchestrator import KarunaOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# Session storage (di production, gunakan Redis atau database)
_sessions = {}


def get_or_create_orchestrator(session_id: Optional[str] = None) -> KarunaOrchestrator:
    """Ambil atau buat orchestrator untuk session."""
    from s2_emotion.emotion_engine import EmotionEngine

    if session_id and session_id in _sessions:
        return _sessions[session_id]

    # Lazy load emotion engine
    emotion_engine = EmotionEngine("models/emotion_engine/final")
    orchestrator = KarunaOrchestrator(emotion_engine)

    if session_id:
        _sessions[session_id] = orchestrator

    return orchestrator


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Kirim pesan dan terima respons dari KarunaAI.

    Endpoint utama yang mengintegrasikan semua komponen:
    - S1: Generative AI response (Groq)
    - S2: Emotion detection
    - S3: Crisis detection
    """
    try:
        # Ambil atau buat session
        session_id = request.session_id or str(uuid.uuid4())

        # Ambil orchestrator
        orch = get_or_create_orchestrator(session_id)

        # Proses pesan melalui pipeline
        result = orch.process(request.message)

        # Bangun response
        return ChatResponse(
            response=result.ai_response,
            emotion={
                "dominant": result.emotion_result.dominant,
                "score": result.emotion_result.score,
                "distribution": result.emotion_result.distribution,
                "topics": result.emotion_result.topics,
                "distress_score": result.emotion_result.distress_score
            },
            crisis={
                "level": result.cds_result.level,
                "score": result.cds_result.score,
                "triggers": result.cds_result.triggers,
                "detail": result.cds_result.detail
            },
            session_id=session_id,
            message_count=orch.msg_count,
            crisis_banner=result.crisis_banner,
            validator_note=result.validator_note
        )

    except Exception as e:
        logger.error(f"Error in /chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.post("/chat/validate")
async def validate_response(response: str, cds_level: str = "NORMAL"):
    """
    Validasi respons AI untuk memastikan kualitas.

    Args:
        response: Respons AI yang akan divalidasi
        cds_level: Level krisis saat ini
    """
    from s1_conversational.output_validator import validate

    is_valid, reason = validate(response, cds_level=cds_level)

    return {
        "is_valid": is_valid,
        "reason": reason
    }
