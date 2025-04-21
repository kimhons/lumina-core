"""
Central Orchestration Service for Lumina AI.

This module implements the core orchestration service that coordinates
between all specialized agents and manages the execution flow.
"""

from typing import Dict, List, Optional, Any
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OrchestrationService:
    """
    Central orchestration service for Lumina AI.
    
    This service coordinates between all specialized agents and manages
    the execution flow of the system. It handles message routing, provider
    selection, and task delegation.
    """
    
    def __init__(self):
        """Initialize the orchestration service."""
        self.conversation_id = str(uuid.uuid4())
        self.providers = {}
        self.tools = {}
        self.memory = None
        self.security = None
        self.started_at = datetime.now()
        logger.info(f"Orchestration service initialized with ID: {self.conversation_id}")
    
    def register_provider(self, provider_id: str, provider: Any) -> None:
        """
        Register an AI provider with the orchestration service.
        
        Args:
            provider_id: Unique identifier for the provider
            provider: Provider instance implementing the BaseProvider interface
        """
        self.providers[provider_id] = provider
        logger.info(f"Provider registered: {provider_id}")
    
    def register_tool(self, tool_id: str, tool: Any) -> None:
        """
        Register a tool with the orchestration service.
        
        Args:
            tool_id: Unique identifier for the tool
            tool: Tool instance implementing the BaseTool interface
        """
        self.tools[tool_id] = tool
        logger.info(f"Tool registered: {tool_id}")
    
    def set_memory(self, memory: Any) -> None:
        """
        Set the memory system for the orchestration service.
        
        Args:
            memory: Memory system implementing the BaseMemory interface
        """
        self.memory = memory
        logger.info("Memory system set")
    
    def set_security(self, security: Any) -> None:
        """
        Set the security system for the orchestration service.
        
        Args:
            security: Security system implementing the BaseSecurity interface
        """
        self.security = security
        logger.info("Security system set")
    
    def process_message(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            message: The user message to process
            user_id: The ID of the user sending the message
            context: Optional context information for the message
            
        Returns:
            A dictionary containing the response and metadata
        """
        # Validate user permissions
        if self.security and not self.security.validate_user(user_id):
            logger.warning(f"Unauthorized access attempt by user: {user_id}")
            return {"error": "Unauthorized"}
        
        # Store message in memory
        if self.memory:
            self.memory.store_message("user", message, user_id, context)
        
        # Analyze message to determine task complexity and requirements
        task_analysis = self._analyze_task(message, context)
        
        # Select the most appropriate provider based on task analysis
        provider = self._select_provider(task_analysis)
        if not provider:
            logger.error("No suitable provider available for the task")
            return {"error": "No suitable provider available"}
        
        # Process message with selected provider
        try:
            response = provider.process_message(message, context)
            
            # Store response in memory
            if self.memory:
                self.memory.store_message("assistant", response["content"], user_id, context)
            
            # Add metadata to response
            response["timestamp"] = datetime.now().isoformat()
            response["conversation_id"] = self.conversation_id
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {"error": f"Error processing message: {str(e)}"}
    
    def _analyze_task(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the task to determine complexity and requirements.
        
        Args:
            message: The user message to analyze
            context: Optional context information
            
        Returns:
            A dictionary containing task analysis results
        """
        # Simple implementation for now - will be enhanced with NLP-based analysis
        analysis = {
            "complexity": "medium",
            "requires_reasoning": True,
            "requires_code": False,
            "requires_tools": False,
            "domain": "general"
        }
        
        # Check for code-related keywords
        if any(keyword in message.lower() for keyword in ["code", "function", "programming", "python", "javascript"]):
            analysis["requires_code"] = True
            analysis["complexity"] = "high"
        
        # Check for tool-related keywords
        if any(keyword in message.lower() for keyword in ["search", "browse", "calculate", "find", "look up"]):
            analysis["requires_tools"] = True
        
        return analysis
    
    def _select_provider(self, task_analysis: Dict[str, Any]) -> Optional[Any]:
        """
        Select the most appropriate provider for the given task.
        
        Args:
            task_analysis: Analysis of the task requirements
            
        Returns:
            The selected provider or None if no suitable provider is available
        """
        if not self.providers:
            logger.warning("No providers registered")
            return None
        
        # Simple implementation for now - will be enhanced with sophisticated selection logic
        # For high complexity tasks requiring code, prefer OpenAI
        if task_analysis["complexity"] == "high" and task_analysis["requires_code"]:
            if "openai" in self.providers:
                return self.providers["openai"]
        
        # For tasks requiring tools, prefer Claude
        if task_analysis["requires_tools"]:
            if "claude" in self.providers:
                return self.providers["claude"]
        
        # Default to the first available provider
        return next(iter(self.providers.values()))
