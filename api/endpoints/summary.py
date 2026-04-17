# api/endpoints/summary.py
# Summary endpoint - untuk generate ringkasan sesi

from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary/{session_id}")
async def get_summary(session_id: str):
    """
    Ambil ringkasan dari session yang sudah berakhir.

    Session harus diakhiri terlebih dahulu melalui /session/end.
    """
    # Import session storage dari chat endpoint
    from api.endpoints.chat import _sessions

    if session_id not in _sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    orch = _sessions[session_id]

    if not orch.session_ended or orch.summary is None:
        raise HTTPException(
            status_code=400,
            detail="Session belum diakhiri. Gunakan /session/end terlebih dahulu."
        )

    return {
        "session_id": session_id,
        "summary": orch.summary.paragraf,
        "flag": orch.summary.flag,
        "flag_reasoning": orch.summary.flag_reasoning,
        "tren_distress": orch.summary.tren_distress,
        "jumlah_pesan": orch.summary.jumlah_pesan
    }
