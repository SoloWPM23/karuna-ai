# api/main.py
# KarunaAI REST API Server
# FastAPI application untuk melayani semua endpoint

import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import endpoint routers
from api.endpoints import chat, emotion, crisis, summary, tts, stt, session, voices, models_info
from api.utils.security import verify_api_key

# -- API Key Security --
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(request: Request, api_key: str = Depends(API_KEY_HEADER)):
    """Verifikasi API key untuk protected endpoints."""
    # Skip verifikasi jika API key tidak diaktifkan (development mode)
    if not os.getenv("API_KEY_ENABLED") or os.getenv("API_KEY_ENABLED") == "false":
        return True

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")

    return True


# -- Lifespan Events --
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup dan shutdown events."""
    # Startup
    logger.info("Starting KarunaAI API Server...")

    # Inisialisasi model (lazy loading)
    from s2_emotion.emotion_engine import EmotionEngine
    from s3_crisis.cds_engine import analyze_crisis

    # Simpan di app state
    app.state.emotion_engine = None
    app.state.crisis_analyzer = analyze_crisis

    logger.info("KarunaAI API Server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down KarunaAI API Server...")


# -- Create FastAPI App --
app = FastAPI(
    title="KarunaAI API",
    description="REST API untuk KarunaAI - AI Companion untuk Curhat Mental Health",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# -- CORS Middleware --
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Include Routers --
app.include_router(
    chat.router,
    prefix="/api/v1",
    tags=["Chat"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    emotion.router,
    prefix="/api/v1",
    tags=["Emotion"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    crisis.router,
    prefix="/api/v1",
    tags=["Crisis"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    summary.router,
    prefix="/api/v1",
    tags=["Summary"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    tts.router,
    prefix="/api/v1",
    tags=["TTS"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    stt.router,
    prefix="/api/v1",
    tags=["STT"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    session.router,
    prefix="/api/v1",
    tags=["Session"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    voices.router,
    prefix="/api/v1",
    tags=["Voices"],
)
app.include_router(
    models_info.router,
    prefix="/api/v1",
    tags=["Models"],
)


# -- Health Check --
@app.get("/health", tags=["Health"])
async def health_check():
    """Cek apakah API sedang berjalan."""
    return {"status": "healthy", "service": "karunaai-api"}


# -- Rate Limiter --
rate_limit_store = defaultdict(list)


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    """Rate limiting sederhana per IP."""
    if os.getenv("RATE_LIMIT_ENABLED") == "true":
        client_ip = request.client.host
        now = datetime.now()
        window = timedelta(minutes=1)
        limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

        # Bersihkan entry lama
        rate_limit_store[client_ip] = [
            t for t in rate_limit_store[client_ip] if t > now - window
        ]

        if len(rate_limit_store[client_ip]) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )

        rate_limit_store[client_ip].append(now)

    response = await call_next(request)
    return response


# -- Error Handlers --
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "Something went wrong"
        }
    )
