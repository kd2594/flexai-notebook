"""
Session Manager
Manages user sessions and compute instance mappings
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)


class Session(BaseModel):
    """User Session"""
    session_id: str
    user_id: Optional[str] = None
    instance_id: Optional[str] = None
    gpu_type: Optional[str] = None
    gpu_count: int = 0
    status: str  # "created", "provisioning", "active", "stopped"
    created_at: datetime
    expires_at: datetime
    last_activity: datetime


class SessionManager:
    """Manages user sessions and compute instances"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.cleanup_task = None
    
    async def start(self):
        """Start the session manager"""
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        logger.info("Session manager started")
    
    async def stop(self):
        """Stop the session manager"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Session manager stopped")
    
    def create_session(self, user_id: Optional[str] = None, ttl_hours: int = 24) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            status="created",
            created_at=now,
            expires_at=now + timedelta(hours=ttl_hours),
            last_activity=now
        )
        
        self.sessions[session_id] = session
        if user_id:
            self.user_sessions[user_id] = session_id
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = datetime.utcnow()
        return session
    
    def get_user_session(self, user_id: str) -> Optional[Session]:
        """Get a user's active session"""
        session_id = self.user_sessions.get(user_id)
        if session_id:
            return self.get_session(session_id)
        return None
    
    def update_session(
        self,
        session_id: str,
        instance_id: Optional[str] = None,
        gpu_type: Optional[str] = None,
        gpu_count: Optional[int] = None,
        status: Optional[str] = None
    ) -> Optional[Session]:
        """Update session details"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if instance_id is not None:
            session.instance_id = instance_id
        if gpu_type is not None:
            session.gpu_type = gpu_type
        if gpu_count is not None:
            session.gpu_count = gpu_count
        if status is not None:
            session.status = status
        
        session.last_activity = datetime.utcnow()
        logger.info(f"Updated session {session_id}")
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        if session.user_id and self.user_sessions.get(session.user_id) == session_id:
            del self.user_sessions[session.user_id]
        
        del self.sessions[session_id]
        logger.info(f"Deleted session {session_id}")
        return True
    
    def extend_session(self, session_id: str, hours: int = 1) -> Optional[Session]:
        """Extend session expiration"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        session.expires_at += timedelta(hours=hours)
        session.last_activity = datetime.utcnow()
        logger.info(f"Extended session {session_id} by {hours} hours")
        return session
    
    def get_all_sessions(self) -> Dict[str, Session]:
        """Get all active sessions"""
        return self.sessions.copy()
    
    async def _cleanup_expired_sessions(self):
        """Periodically cleanup expired sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                now = datetime.utcnow()
                expired_sessions = [
                    session_id
                    for session_id, session in self.sessions.items()
                    if session.expires_at < now
                ]
                
                for session_id in expired_sessions:
                    logger.info(f"Cleaning up expired session {session_id}")
                    self.delete_session(session_id)
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")


# Global session manager instance
session_manager = SessionManager()
