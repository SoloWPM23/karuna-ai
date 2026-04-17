# api/endpoints/session.py
# Session management endpoints

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Session storage (di production, gunakan database)
_sessions = {}


class StartSessionResponse(BaseModel):
    session_id: str
    message: str


class EndSessionRequest(BaseModel):
    session_id: str


class EndSessionResponse(BaseModel):
    session_id: str
    summary: str
    flag: str
    flag_reasoning: str
    emotion_timeline: list
    cds_level: str


@router.post("/session/start", response_model=StartSessionResponse)
async def start_session():
    """
    Mulai sesi baru dengan KarunaAI.

    Returns:
        Session ID yang dapat digunakan untuk percakapan
    """
    session_id = str(uuid.uuid4())

    # Inisialisasi orchestrator
    from s2_emotion.emotion_engine import EmotionEngine
    from pipeline.orchestrator import KarunaOrchestrator

    emotion_engine = EmotionEngine("models/emotion_engine/final")
    orchestrator = KarunaOrchestrator(emotion_engine)

    _sessions[session_id] = orchestrator

    # Sinkronisasi dengan chat endpoint sessions
    from api.endpoints.chat import _sessions as chat_sessions
    chat_sessions[session_id] = orchestrator

    return StartSessionResponse(
        session_id=session_id,
        message="Sesi baru dimulai. Karuna siap mendengarkan."
    )


@router.post("/session/end", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest):
    """
    Akhiri sesi dan dapatkan ringkasan.
    """
    # Cek di session storage lokal dan chat endpoint
    from api.endpoints.chat import _sessions as chat_sessions

    orch = _sessions.get(request.session_id) or chat_sessions.get(request.session_id)

    if orch is None:
        raise HTTPException(
            status_code=404,
            detail="Session tidak ditemukan"
        )

    # Akhiri sesi
    summary = orch.end_session()

    if summary is None:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada pesan dalam sesi"
        )

    # Hapus dari storage
    _sessions.pop(request.session_id, None)
    chat_sessions.pop(request.session_id, None)

    return EndSessionResponse(
        session_id=request.session_id,
        summary=summary.paragraf,
        flag=summary.flag,
        flag_reasoning=summary.flag_reasoning,
        emotion_timeline=[
            {
                "dominant": e.dominant,
                "distress": e.distress_score
            }
            for e in orch.emotion_history
        ],
        cds_level=summary.cds_level_akhir
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Ambil state session saat ini."""
    from api.endpoints.chat import _sessions as chat_sessions

    orch = _sessions.get(session_id) or chat_sessions.get(session_id)

    if orch is None:
        raise HTTPException(
            status_code=404,
            detail="Session tidak ditemukan"
        )

    return {
        "session_id": session_id,
        "message_count": orch.msg_count,
        "emotion_history": [
            {
                "dominant": e.dominant,
                "distress": e.distress_score
            }
            for e in orch.emotion_history
        ],
        "last_cds": {
            "level": orch.last_cds_result.level,
            "score": orch.last_cds_result.score
        } if orch.last_cds_result else None
    }
