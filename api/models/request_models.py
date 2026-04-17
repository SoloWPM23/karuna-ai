# api/models/request_models.py
# Pydantic models untuk request dan response

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    emotion: Dict
    crisis: Dict
    session_id: str
    message_count: int
    crisis_banner: str = ""


class EmotionRequest(BaseModel):
    text: str = Field(..., min_length=1)
    return_topics: bool = True


class EmotionResponse(BaseModel):
    dominant: str
    score: float
    distribution: Dict
    topics: Optional[List[str]] = None
    distress_score: float


class CrisisRequest(BaseModel):
    text: str = Field(..., min_length=1)
    emotion_history: Optional[List[Dict]] = None


class CrisisResponse(BaseModel):
    level: str
    score: float
    triggers: List[str]
    detail: Optional[Dict] = None


class SummaryResponse(BaseModel):
    session_id: str
    summary: str
    flag: str
    flag_reasoning: str
    tren_distress: str
    jumlah_pesan: int


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "sarah"
    mood: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class TTSResponse(BaseModel):
    audio: str
    format: str


class STTRequest(BaseModel):
    audio: str
    language: str = "id"


class STTResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
