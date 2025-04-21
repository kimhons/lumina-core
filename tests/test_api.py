"""
Tests for the API gateway.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from lumina.api.gateway import APIGateway, MessageRequest

class TestAPIGateway:
    """Tests for the APIGateway class."""
    
    @pytest.fixture
    def orchestration_service(self):
        """Create a mock orchestration service."""
        service = MagicMock()
        service.conversation_id = "test-conversation-id"
        service.process_message.return_value = {
            "content": "Test response",
            "provider": "test-provider",
            "model": "test-model",
            "conversation_id": "test-conversation-id",
            "timestamp": "2025-04-21T12:00:00",
            "tokens": {"prompt": 10, "completion": 20, "total": 30}
        }
        return service
    
    @pytest.fixture
    def api_gateway(self, orchestration_service):
        """Create an API gateway with a mock orchestration service."""
        return APIGateway(orchestration_service)
    
    @pytest.fixture
    def client(self, api_gateway):
        """Create a test client for the FastAPI app."""
        return TestClient(api_gateway.app)
    
    def test_process_message_endpoint(self, client, orchestration_service):
        """Test the process_message endpoint."""
        # Mock token validation to always return True
        with patch.object(APIGateway, '_validate_token', return_value=True):
            response = client.post(
                "/api/messages",
                json={"message": "Hello", "user_id": "test-user"},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "Test response"
            assert data["provider"] == "test-provider"
            assert data["model"] == "test-model"
            assert data["conversation_id"] == "test-conversation-id"
            assert data["timestamp"] == "2025-04-21T12:00:00"
            assert data["tokens"] == {"prompt": 10, "completion": 20, "total": 30}
            
            orchestration_service.process_message.assert_called_once_with(
                "Hello", "test-user", None
            )
    
    def test_process_message_with_context(self, client, orchestration_service):
        """Test the process_message endpoint with context."""
        # Mock token validation to always return True
        with patch.object(APIGateway, '_validate_token', return_value=True):
            context = {"conversation_history": ["Previous message"]}
            response = client.post(
                "/api/messages",
                json={"message": "Hello", "user_id": "test-user", "context": context},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            orchestration_service.process_message.assert_called_once_with(
                "Hello", "test-user", context
            )
    
    def test_process_message_unauthorized(self, client):
        """Test the process_message endpoint with invalid token."""
        response = client.post(
            "/api/messages",
            json={"message": "Hello", "user_id": "test-user"}
        )
        
        assert response.status_code == 401
    
    def test_process_message_error(self, client, orchestration_service):
        """Test the process_message endpoint when an error occurs."""
        # Mock token validation to always return True
        with patch.object(APIGateway, '_validate_token', return_value=True):
            # Set up orchestration service to return an error
            orchestration_service.process_message.return_value = {
                "error": "Test error"
            }
            
            response = client.post(
                "/api/messages",
                json={"message": "Hello", "user_id": "test-user"},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["error"] == "Test error"
            assert data["content"] == ""
    
    def test_token_validation(self, api_gateway):
        """Test token validation."""
        # Test valid token
        assert api_gateway._validate_token("valid-token-12345", "test-user") == True
        
        # Test invalid token (too short)
        assert api_gateway._validate_token("short", "test-user") == False
        
        # Test None token
        assert api_gateway._validate_token(None, "test-user") == False
