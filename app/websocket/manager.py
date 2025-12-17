from typing import Dict, List, Set
from fastapi import WebSocket

class ConnectionManager:
    """Manager for WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection and add to session"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        print(f"Client connected to session {session_id}. Total connections: {len(self.active_connections[session_id])}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection from session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_message(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast message to all connections in a session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id].copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to connection: {e}")
                    self.disconnect(connection, session_id)
    
    async def get_session_connections(self, session_id: str) -> List[WebSocket]:
        """Get all connections for a session"""
        if session_id in self.active_connections:
            return list(self.active_connections[session_id])
        return []