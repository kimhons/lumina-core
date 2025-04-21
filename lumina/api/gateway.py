"""
API Gateway for Lumina AI.

This module implements the API gateway that exposes Lumina AI capabilities
to clients through HTTP and WebSocket interfaces.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Models for request and response
class MessageRequest(BaseModel):
    """Model for incoming message requests."""
    message: str
    user_id: str
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    """Model for outgoing message responses."""
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    conversation_id: str
    timestamp: str
    tokens: Optional[Dict[str, int]] = None
    error: Optional[str] = None

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class APIGateway:
    """
    API Gateway for Lumina AI.
    
    This class implements the API gateway that exposes Lumina AI capabilities
    to clients through HTTP and WebSocket interfaces.
    """
    
    def __init__(self, orchestration_service):
        """
        Initialize the API gateway.
        
        Args:
            orchestration_service: The central orchestration service
        """
        self.orchestration_service = orchestration_service
        self.app = FastAPI(title="Lumina AI API", version="0.1.0")
        self.active_connections = {}
        self._setup_routes()
        logger.info("API Gateway initialized")
    
    def _setup_routes(self):
        """Set up API routes."""
        
        @self.app.post("/api/messages", response_model=MessageResponse)
        async def process_message(
            request: MessageRequest,
            token: str = Depends(oauth2_scheme)
        ):
            """
            Process a message through the Lumina AI system.
            
            Args:
                request: The message request
                token: Authentication token
                
            Returns:
                The message response
            """
            # Validate token (simplified for now)
            if not self._validate_token(token, request.user_id):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Process message through orchestration service
            try:
                response = self.orchestration_service.process_message(
                    request.message,
                    request.user_id,
                    request.context
                )
                
                # Handle error responses
                if "error" in response:
                    return MessageResponse(
                        content="",
                        conversation_id=self.orchestration_service.conversation_id,
                        timestamp=datetime.now().isoformat(),
                        error=response["error"]
                    )
                
                # Return successful response
                return MessageResponse(
                    content=response["content"],
                    provider=response.get("provider"),
                    model=response.get("model"),
                    conversation_id=response["conversation_id"],
                    timestamp=response["timestamp"],
                    tokens=response.get("tokens")
                )
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                return MessageResponse(
                    content="",
                    conversation_id=self.orchestration_service.conversation_id,
                    timestamp=datetime.now().isoformat(),
                    error=f"Internal server error: {str(e)}"
                )
        
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            """
            WebSocket endpoint for real-time communication.
            
            Args:
                websocket: The WebSocket connection
                client_id: Client identifier
            """
            await self._handle_websocket_connection(websocket, client_id)
    
    async def _handle_websocket_connection(self, websocket: WebSocket, client_id: str):
        """
        Handle a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection
            client_id: Client identifier
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connection established for client: {client_id}")
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Validate message format
                if "message" not in message_data or "user_id" not in message_data:
                    await websocket.send_json({
                        "error": "Invalid message format. Must include 'message' and 'user_id'."
                    })
                    continue
                
                # Process message through orchestration service
                response = self.orchestration_service.process_message(
                    message_data["message"],
                    message_data["user_id"],
                    message_data.get("context")
                )
                
                # Send response back to client
                await websocket.send_json(response)
        except WebSocketDisconnect:
            # Remove connection when client disconnects
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            logger.info(f"WebSocket connection closed for client: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {str(e)}")
            # Attempt to send error message
            try:
                await websocket.send_json({
                    "error": f"Server error: {str(e)}"
                })
            except:
                pass
            
            # Remove connection on error
            if client_id in self.active_connections:
                del self.active_connections[client_id]
    
    def _validate_token(self, token: str, user_id: str) -> bool:
        """
        Validate authentication token.
        
        Args:
            token: Authentication token
            user_id: User identifier
            
        Returns:
            True if token is valid, False otherwise
        """
        # Simplified token validation for now
        # In a production system, this would validate against a proper auth system
        return token is not None and len(token) > 10
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the API gateway.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        logger.info(f"Starting API Gateway on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)
