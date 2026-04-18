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
    validator_note: str = ""


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
    layer1_level: Optional[str] = None
    layer1_confidence: Optional[float] = None
    layer2_label: Optional[str] = None
    layer2_confidence: Optional[float] = None
    layer3_score: Optional[float] = None
    layer3_patterns: Optional[List[str]] = None
    detail: Optional[Dict] = None


class SummaryResponse(BaseModel):
    session_id: str
    summary: str
    flag: str
    flag_reasoning: str
    pesan_penutup: str
    tren_distress: str
    distress_awal: float
    distress_akhir: float
    jumlah_pesan: int


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "sarah"
    mood: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    stability: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    similarity_boost: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    style: Optional[float] = Field(default=None, ge=0.0, le=1.0)


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
