# app.py
# KarunaAI API - Entry point untuk HuggingFace Spaces (Docker SDK)
# Menggabungkan FastAPI backend dengan Gradio UI untuk demo

import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import gradio as gr
from api.main import app as fastapi_app

# Override: matikan API key di Spaces (gunakan HF auth jika perlu)
os.environ.setdefault("API_KEY_ENABLED", "false")

# -- Gradio Demo UI --
# UI sederhana yang muncul di halaman Space untuk testing manual

def analyze_emotion(text):
    """Wrapper untuk demo emotion detection di Gradio UI."""
    if not text or not text.strip():
        return {"error": "Teks tidak boleh kosong"}
    try:
        from s2_emotion.emotion_engine import EmotionEngine
        engine = EmotionEngine("models/emotion_engine/final")
        result = engine.analyze(text)
        return {
            "dominant": result.dominant,
            "score": round(result.score, 4),
            "distribution": {k: round(v, 4) for k, v in result.distribution.items()},
            "distress_score": round(result.distress_score, 4)
        }
    except Exception as e:
        return {"error": str(e)}


def detect_crisis(text):
    """Wrapper untuk demo crisis detection di Gradio UI."""
    if not text or not text.strip():
        return {"error": "Teks tidak boleh kosong"}
    try:
        from s3_crisis.cds_engine import analyze_crisis
        result = analyze_crisis(text, [])
        return {
            "level": result.level,
            "score": round(result.score, 4),
            "triggers": result.triggers,
            "detail": result.detail
        }
    except Exception as e:
        return {"error": str(e)}


# Gradio Blocks UI
with gr.Blocks(title="KarunaAI API") as demo:
    gr.Markdown("# KarunaAI API")
    gr.Markdown(
        "REST API untuk KarunaAI - AI Companion untuk Curhat Mental Health.\n\n"
        "Dokumentasi lengkap: [/docs](/docs) | [/redoc](/redoc)"
    )

    with gr.Tab("Emotion Detection"):
        emo_input = gr.Textbox(label="Masukkan teks", placeholder="Aku merasa sedih hari ini...")
        emo_output = gr.JSON(label="Hasil Analisis Emosi")
        emo_btn = gr.Button("Deteksi Emosi")
        emo_btn.click(analyze_emotion, inputs=emo_input, outputs=emo_output)

    with gr.Tab("Crisis Detection"):
        cris_input = gr.Textbox(label="Masukkan teks", placeholder="Aku merasa tidak berguna...")
        cris_output = gr.JSON(label="Hasil Deteksi Krisis")
        cris_btn = gr.Button("Deteksi Krisis")
        cris_btn.click(detect_crisis, inputs=cris_input, outputs=cris_output)

    gr.Markdown("---")
    gr.Markdown(
        "### API Endpoints\n"
        "- `POST /api/v1/chat` - Chat dengan KarunaAI\n"
        "- `POST /api/v1/emotion` - Deteksi emosi\n"
        "- `POST /api/v1/crisis` - Deteksi krisis\n"
        "- `GET /api/v1/voices` - Daftar voice TTS\n"
        "- `POST /api/v1/tts` - Text to Speech\n"
        "- `POST /api/v1/stt` - Speech to Text\n"
    )

# Mount Gradio ke FastAPI app
app = gr.mount_gradio_app(fastapi_app, demo, path="/ui")
