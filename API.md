# KarunaAI API Documentation

## Base URL

```
https://your-api.onrender.com/api/v1
```

## Authentication

Jika API key diaktifkan, tambahkan header:

```
X-API-Key: your_api_key
```

## Endpoints

### 1. Chat -- Kirim Pesan

```bash
curl -X POST https://your-api.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"message": "Aku merasa lelah"}'
```

**Response:**
```json
{
  "response": "Aku mendengar...",
  "emotion": {
    "dominant": "sedih",
    "score": 0.75,
    "distribution": {"sedih": 0.75, "senang": 0.05, "marah": 0.05, "takut": 0.05, "kaget": 0.03, "jijik": 0.02, "netral": 0.05},
    "topics": ["self"],
    "distress_score": 0.6
  },
  "crisis": {
    "level": "NORMAL",
    "score": 0.1,
    "triggers": []
  },
  "session_id": "abc123-def456",
  "message_count": 1,
  "crisis_banner": ""
}
```

### 2. Emotion -- Deteksi Emosi

```bash
curl -X POST https://your-api.onrender.com/api/v1/emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "Aku senang bisa ketemu kamu"}'
```

**Response:**
```json
{
  "dominant": "senang",
  "score": 0.85,
  "distribution": {"senang": 0.85, "sedih": 0.03, "marah": 0.02, "takut": 0.02, "kaget": 0.03, "jijik": 0.01, "netral": 0.04},
  "topics": ["relationship"],
  "distress_score": 0.1
}
```

### 3. Crisis -- Deteksi Krisis

```bash
curl -X POST https://your-api.onrender.com/api/v1/crisis \
  -H "Content-Type: application/json" \
  -d '{"text": "Aku mau bunuh diri"}'
```

**Response:**
```json
{
  "level": "L3",
  "score": 0.95,
  "triggers": ["L1_keyword_L3"],
  "detail": {
    "l1_level": "L3",
    "l1_conf": 1.0,
    "l2_skipped": true,
    "l3_skipped": true
  }
}
```

### 4. Session -- Mulai dan Akhiri Sesi

**Mulai sesi:**
```bash
curl -X POST https://your-api.onrender.com/api/v1/session/start
```

**Akhiri sesi:**
```bash
curl -X POST https://your-api.onrender.com/api/v1/session/end \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123-def456"}'
```

### 5. TTS -- Teks ke Audio

```bash
curl -X POST https://your-api.onrender.com/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Halo, aku Karuna", "voice": "sarah"}'
```

**Response:**
```json
{
  "audio": "base64_encoded_audio...",
  "format": "mp3"
}
```

### 6. STT -- Audio ke Teks

```bash
curl -X POST https://your-api.onrender.com/api/v1/stt \
  -H "Content-Type: application/json" \
  -d '{"audio": "base64_encoded_audio"}'
```

**Response:**
```json
{
  "text": "Aku merasa sangat lelah akhir-akhir ini...",
  "language": "id"
}
```

### 7. Voices -- Daftar Suara TTS

```bash
curl https://your-api.onrender.com/api/v1/voices
```

### 8. Models -- Info Model

```bash
curl https://your-api.onrender.com/api/v1/models/info
```

### 9. Health Check

```bash
curl https://your-api.onrender.com/health
```

## Error Codes

| Code | Keterangan |
|------|------------|
| 400 | Bad Request - input tidak valid |
| 401 | Unauthorized - API key diperlukan |
| 403 | Forbidden - API key tidak valid |
| 429 | Too Many Requests - rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limits

- Default: 60 requests/menit
- Per API key: 1000 requests/jam

## Contoh Integrasi

### Python

```python
import requests

BASE_URL = "https://your-api.onrender.com/api/v1"

def chat(message):
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message},
        headers={"X-API-Key": "your_api_key"}
    )
    return response.json()

result = chat("Aku merasa lelah")
print(result["response"])
```

### JavaScript

```javascript
const response = await fetch('https://your-api.onrender.com/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your_api_key'
  },
  body: JSON.stringify({ message: 'Aku merasa lelah' })
});

const result = await response.json();
console.log(result.response);
```

### cURL

```bash
# Chat
curl -X POST https://your-api.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Halo"}'

# Emotion detection
curl -X POST https://your-api.onrender.com/api/v1/emotion \
  -H "Content-Type: application/json" \
  -d '{"text": "Aku senang"}'

# TTS
curl -X POST https://your-api.onrender.com/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Halo", "voice": "sarah"}'
```
