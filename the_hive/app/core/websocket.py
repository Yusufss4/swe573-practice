"""
WebSocket manager for real-time notifications.
# SRS NFR-N.1: WebSocket connections for real-time notification delivery
"""
from collections.abc import Generator
from typing import Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.
    # SRS NFR-N.2: Track active connections per user
    """
    def __init__(self):
        # Map of user_id to WebSocket connection
        self.active_connections: dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept WebSocket connection and store it."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, user_id: int):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_notification(self, user_id: int, notification_data: dict):
        """
        Send notification to specific user if they're connected.
        # SRS FR-N.4: Deliver notifications via WebSocket
        """
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(
                    json.dumps(notification_data)
                )
                logger.info(f"Sent notification to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast(self, user_ids: list[int], notification_data: dict):
        """Send notification to multiple users."""
        for user_id in user_ids:
            await self.send_notification(user_id, notification_data)


# Global connection manager instance
manager = ConnectionManager()
