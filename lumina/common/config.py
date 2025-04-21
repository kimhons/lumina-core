"""
Configuration management for Lumina AI.

This module provides configuration management functionality for Lumina AI,
including loading configuration from environment variables and configuration files.
"""

import os
import json
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

from lumina.common.utils import load_config, merge_dicts

logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

class ConfigManager:
    """
    Configuration manager for Lumina AI.
    
    This class manages configuration settings from multiple sources,
    including environment variables and configuration files.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Optional path to a configuration file
        """
        self.config = {}
        self.config_path = config_path
        
        # Load configuration from file if provided
        if config_path:
            self._load_from_file(config_path)
        
        # Load configuration from environment variables
        self._load_from_env()
        
        logger.info("Configuration manager initialized")
    
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        file_config = load_config(config_path)
        self.config = merge_dicts(self.config, file_config)
        logger.info(f"Loaded configuration from {config_path}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_config = {}
        
        # Provider API keys
        providers = {
            "OPENAI_API_KEY": "providers.openai.api_key",
            "CLAUDE_API_KEY": "providers.claude.api_key",
            "GEMINI_API_KEY": "providers.gemini.api_key",
            "DEEPSEEK_API_KEY": "providers.deepseek.api_key",
            "GROK_API_KEY": "providers.grok.api_key"
        }
        
        for env_var, config_key in providers.items():
            if os.environ.get(env_var):
                self._set_nested_key(env_config, config_key, os.environ.get(env_var))
        
        # API configuration
        if os.environ.get("API_HOST"):
            self._set_nested_key(env_config, "api.host", os.environ.get("API_HOST"))
        
        if os.environ.get("API_PORT"):
            try:
                port = int(os.environ.get("API_PORT", "8000"))
                self._set_nested_key(env_config, "api.port", port)
            except ValueError:
                logger.warning(f"Invalid API_PORT value: {os.environ.get('API_PORT')}")
        
        # Security configuration
        if os.environ.get("JWT_SECRET"):
            self._set_nested_key(env_config, "security.jwt_secret", os.environ.get("JWT_SECRET"))
        
        # Log level
        if os.environ.get("LOG_LEVEL"):
            self._set_nested_key(env_config, "logging.level", os.environ.get("LOG_LEVEL"))
        
        # Merge environment configuration
        self.config = merge_dicts(self.config, env_config)
        logger.info("Loaded configuration from environment variables")
    
    def _set_nested_key(self, config_dict: Dict[str, Any], key_path: str, value: Any) -> None:
        """
        Set a nested key in a dictionary.
        
        Args:
            config_dict: The dictionary to modify
            key_path: The path to the key, using dot notation (e.g., "providers.openai.api_key")
            value: The value to set
        """
        keys = key_path.split('.')
        current = config_dict
        
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                current[key] = value
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key_path: The path to the key, using dot notation (e.g., "providers.openai.api_key")
            default: Default value to return if the key is not found
            
        Returns:
            The configuration value, or the default if not found
        """
        keys = key_path.split('.')
        current = self.config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key_path: The path to the key, using dot notation (e.g., "providers.openai.api_key")
            value: The value to set
        """
        self._set_nested_key(self.config, key_path, value)
    
    def save(self, config_path: Optional[str] = None) -> bool:
        """
        Save the configuration to a file.
        
        Args:
            config_path: Path to save the configuration file, defaults to the path used during initialization
            
        Returns:
            True if successful, False otherwise
        """
        path = config_path or self.config_path
        if not path:
            logger.warning("No configuration path specified")
            return False
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration.
        
        Returns:
            The complete configuration dictionary
        """
        return self.config.copy()
