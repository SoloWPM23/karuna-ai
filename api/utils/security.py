# api/utils/security.py
# Security utilities untuk API key validation

import os
import hashlib
import secrets
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# API key store (in production, gunakan database)
# Format: {"api_key_hash": {"name": "...", "created": ..., "rate_limit": ...}}
_api_keys = {}


def _init_api_keys():
    """Initialize API keys dari environment variable."""
    keys_env = os.getenv("API_KEYS", "")
    if keys_env:
        for i, key in enumerate(keys_env.split(",")):
            key = key.strip()
            if key:
                key_hash = hashlib.sha256(key.encode()).hexdigest()
                _api_keys[key_hash] = {
                    "name": f"key_{i+1}",
                    "created": datetime.now(),
                    "rate_limit": int(os.getenv("RATE_LIMIT_PER_KEY", "1000"))
                }


_init_api_keys()


def verify_api_key(api_key: str) -> bool:
    """
    Verifikasi API key.

    Args:
        api_key: API key yang akan diverifikasi

    Returns:
        True jika valid, False jika tidak
    """
    if not api_key:
        return False

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return key_hash in _api_keys


def get_api_key_info(api_key: str) -> Optional[dict]:
    """Ambil info dari API key."""
    if not api_key:
        return None

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return _api_keys.get(key_hash)


def generate_api_key(name: str = "default") -> str:
    """
    Generate API key baru.

    Args:
        name: Nama untuk key

    Returns:
        API key baru
    """
    key = f"ka_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    _api_keys[key_hash] = {
        "name": name,
        "created": datetime.now(),
        "rate_limit": int(os.getenv("RATE_LIMIT_PER_KEY", "1000"))
    }

    return key


def revoke_api_key(api_key: str) -> bool:
    """
    Cabut API key.

    Args:
        api_key: Key yang akan dicabut

    Returns:
        True jika berhasil, False jika tidak ditemukan
    """
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if key_hash in _api_keys:
        del _api_keys[key_hash]
        return True

    return False


# -- Input Validation --

def validate_text_input(text: str, max_length: int = 10000) -> bool:
    """
    Validasi teks input untuk keamanan.

    Args:
        text: Teks yang akan divalidasi
        max_length: Panjang maksimum yang diizinkan

    Returns:
        True jika valid
    """
    if not text or len(text) > max_length:
        return False

    # Cek null bytes
    if "\x00" in text:
        return False

    return True


def sanitize_input(text: str) -> str:
    """
    Sanitasi teks input.

    Args:
        text: Teks yang akan disanitasi

    Returns:
        Teks yang sudah disanitasi
    """
    # Hapus null bytes
    text = text.replace("\x00", "")

    # Strip whitespace
    text = text.strip()

    return text
