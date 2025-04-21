"""
Tests for the orchestration service.
"""

import pytest
from unittest.mock import MagicMock
from lumina.orchestration.service import OrchestrationService

class MockProvider:
    """Mock provider for testing."""
    
    def __init__(self, provider_id="mock"):
        self.provider_id = provider_id
    
    def process_message(self, message, context=None):
        """Process a message and return a mock response."""
        return {
            "content": f"Processed by {self.provider_id}: {message}",
            "provider": self.provider_id,
            "model": "mock-model"
        }
    
    def get_capabilities(self):
        """Return mock capabilities."""
        return {
            "provider": self.provider_id,
            "capabilities": {
                "text_generation": True,
                "code_generation": self.provider_id == "openai",
                "reasoning": True,
                "tool_use": self.provider_id == "claude"
            }
        }
    
    def get_cost_estimate(self, message):
        """Return a mock cost estimate."""
        return 0.001 * len(message)

class MockMemory:
    """Mock memory system for testing."""
    
    def __init__(self):
        self.messages = []
    
    def store_message(self, role, content, user_id, context=None):
        """Store a message in memory."""
        self.messages.append({
            "role": role,
            "content": content,
            "user_id": user_id,
            "context": context
        })

class MockSecurity:
    """Mock security system for testing."""
    
    def validate_user(self, user_id):
        """Validate a user ID."""
        return user_id == "valid_user"

class TestOrchestrationService:
    """Tests for the OrchestrationService class."""
    
    def test_initialization(self):
        """Test that the service initializes correctly."""
        service = OrchestrationService()
        assert service.conversation_id is not None
        assert service.providers == {}
        assert service.tools == {}
        assert service.memory is None
        assert service.security is None
        assert service.started_at is not None
    
    def test_register_provider(self):
        """Test registering a provider."""
        service = OrchestrationService()
        provider = MockProvider()
        service.register_provider("mock", provider)
        assert "mock" in service.providers
        assert service.providers["mock"] == provider
    
    def test_register_tool(self):
        """Test registering a tool."""
        service = OrchestrationService()
        tool = MagicMock()
        service.register_tool("mock_tool", tool)
        assert "mock_tool" in service.tools
        assert service.tools["mock_tool"] == tool
    
    def test_set_memory(self):
        """Test setting the memory system."""
        service = OrchestrationService()
        memory = MockMemory()
        service.set_memory(memory)
        assert service.memory == memory
    
    def test_set_security(self):
        """Test setting the security system."""
        service = OrchestrationService()
        security = MockSecurity()
        service.set_security(security)
        assert service.security == security
    
    def test_process_message_with_valid_user(self):
        """Test processing a message with a valid user."""
        service = OrchestrationService()
        provider = MockProvider()
        service.register_provider("mock", provider)
        
        memory = MockMemory()
        service.set_memory(memory)
        
        security = MockSecurity()
        service.set_security(security)
        
        response = service.process_message("Hello", "valid_user")
        
        assert "content" in response
        assert response["content"] == "Processed by mock: Hello"
        assert response["provider"] == "mock"
        assert "timestamp" in response
        assert "conversation_id" in response
        assert len(memory.messages) == 2
        assert memory.messages[0]["role"] == "user"
        assert memory.messages[0]["content"] == "Hello"
        assert memory.messages[1]["role"] == "assistant"
        assert memory.messages[1]["content"] == "Processed by mock: Hello"
    
    def test_process_message_with_invalid_user(self):
        """Test processing a message with an invalid user."""
        service = OrchestrationService()
        provider = MockProvider()
        service.register_provider("mock", provider)
        
        memory = MockMemory()
        service.set_memory(memory)
        
        security = MockSecurity()
        service.set_security(security)
        
        response = service.process_message("Hello", "invalid_user")
        
        assert "error" in response
        assert response["error"] == "Unauthorized"
        assert len(memory.messages) == 0
    
    def test_process_message_with_no_providers(self):
        """Test processing a message with no providers registered."""
        service = OrchestrationService()
        response = service.process_message("Hello", "valid_user")
        assert "error" in response
        assert response["error"] == "No suitable provider available"
    
    def test_provider_selection_for_code_task(self):
        """Test provider selection for a code-related task."""
        service = OrchestrationService()
        openai_provider = MockProvider("openai")
        claude_provider = MockProvider("claude")
        
        service.register_provider("openai", openai_provider)
        service.register_provider("claude", claude_provider)
        
        response = service.process_message("Write a Python function to calculate Fibonacci numbers", "valid_user")
        
        assert "content" in response
        assert "openai" in response["content"]
    
    def test_provider_selection_for_tool_task(self):
        """Test provider selection for a tool-related task."""
        service = OrchestrationService()
        openai_provider = MockProvider("openai")
        claude_provider = MockProvider("claude")
        
        service.register_provider("openai", openai_provider)
        service.register_provider("claude", claude_provider)
        
        response = service.process_message("Search for the latest news about AI", "valid_user")
        
        assert "content" in response
        assert "claude" in response["content"]
