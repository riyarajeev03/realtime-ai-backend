from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class SessionBase(BaseModel):
    """Base model for session data"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool = True
    summary: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()

class SessionEventBase(BaseModel):
    """Base model for session events"""
    session_id: str
    event_type: str
    content: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()

class SessionCreate(SessionBase):
    """Model for creating a session"""
    pass

class SessionEventCreate(SessionEventBase):
    """Model for creating a session event"""
    pass

class SessionResponse(SessionBase):
    """Model for session response"""
    duration_seconds: Optional[float] = None
    
    class Config:
        from_attributes = True

class SessionEventResponse(SessionEventBase):
    """Model for session event response"""
    id: int
    
    class Config:
        from_attributes = True