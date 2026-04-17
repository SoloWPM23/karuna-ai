# api/utils/session_manager.py
# Session management utilities

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class Session:
    """Session object."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.message_count = 0
        self.metadata: Dict = {}


class SessionManager:
    """
    Mengelola user sessions.

    Di production, ganti dengan Redis atau database.
    """

    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

    def create_session(self) -> str:
        """Buat session baru."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Session(session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Ambil session berdasarkan ID."""
        session = self.sessions.get(session_id)

        if session is None:
            return None

        # Cek timeout
        if datetime.now() - session.last_active > self.session_timeout:
            self.delete_session(session_id)
            return None

        return session

    def update_session(self, session_id: str):
        """Update waktu aktif terakhir session."""
        if session_id in self.sessions:
            self.sessions[session_id].last_active = datetime.now()
            self.sessions[session_id].message_count += 1

    def delete_session(self, session_id: str):
        """Hapus session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired(self):
        """Hapus session yang sudah expired."""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session.last_active > self.session_timeout
        ]

        for sid in expired:
            del self.sessions[sid]

        return len(expired)


# Global instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Ambil global session manager."""
    return _session_manager
