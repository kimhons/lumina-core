"""
Base interfaces for Lumina AI components.

This module defines the abstract base classes and interfaces that
must be implemented by various components of the Lumina AI system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseProvider(ABC):
    """
    Base interface for AI providers.
    
    All provider implementations must inherit from this class and
    implement its abstract methods.
    """
    
    @abstractmethod
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: The user message to process
            context: Optional context information
            
        Returns:
            A dictionary containing the response and metadata
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this provider.
        
        Returns:
            A dictionary describing the provider's capabilities
        """
        pass
    
    @abstractmethod
    def get_cost_estimate(self, message: str) -> float:
        """
        Estimate the cost of processing a message with this provider.
        
        Args:
            message: The user message to process
            
        Returns:
            The estimated cost in USD
        """
        pass


class BaseTool(ABC):
    """
    Base interface for tools.
    
    All tool implementations must inherit from this class and
    implement its abstract methods.
    """
    
    @abstractmethod
    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            params: Tool parameters
            context: Optional context information
            
        Returns:
            A dictionary containing the result and metadata
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool.
        
        Returns:
            A dictionary describing the tool's parameters and return values
        """
        pass


class BaseMemory(ABC):
    """
    Base interface for memory systems.
    
    All memory implementations must inherit from this class and
    implement its abstract methods.
    """
    
    @abstractmethod
    def store_message(self, role: str, content: str, user_id: str, 
                     context: Optional[Dict[str, Any]] = None) -> None:
        """
        Store a message in memory.
        
        Args:
            role: The role of the message sender (e.g., "user", "assistant")
            content: The message content
            user_id: The ID of the user
            context: Optional context information
        """
        pass
    
    @abstractmethod
    def get_conversation_history(self, user_id: str, 
                                limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a user.
        
        Args:
            user_id: The ID of the user
            limit: Optional limit on the number of messages to return
            
        Returns:
            A list of messages in chronological order
        """
        pass
    
    @abstractmethod
    def clear_conversation(self, user_id: str) -> None:
        """
        Clear the conversation history for a user.
        
        Args:
            user_id: The ID of the user
        """
        pass


class BaseSecurity(ABC):
    """
    Base interface for security systems.
    
    All security implementations must inherit from this class and
    implement its abstract methods.
    """
    
    @abstractmethod
    def validate_user(self, user_id: str) -> bool:
        """
        Validate a user ID.
        
        Args:
            user_id: The ID of the user to validate
            
        Returns:
            True if the user is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def authenticate_token(self, token: str) -> Optional[str]:
        """
        Authenticate a token and return the associated user ID.
        
        Args:
            token: The authentication token
            
        Returns:
            The user ID if the token is valid, None otherwise
        """
        pass
    
    @abstractmethod
    def authorize_action(self, user_id: str, action: str, 
                        resource: Optional[str] = None) -> bool:
        """
        Authorize an action for a user.
        
        Args:
            user_id: The ID of the user
            action: The action to authorize
            resource: Optional resource identifier
            
        Returns:
            True if the action is authorized, False otherwise
        """
        pass
