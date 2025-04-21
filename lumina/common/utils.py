"""
Utility functions for Lumina AI.

This module provides common utility functions used across the Lumina AI system.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_id(prefix: str = "") -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        A unique identifier string
    """
    return f"{prefix}{uuid.uuid4()}"

def timestamp() -> str:
    """
    Get the current timestamp in ISO 8601 format.
    
    Returns:
        The current timestamp as a string
    """
    return datetime.now().isoformat()

def count_tokens(text: str) -> int:
    """
    Count the approximate number of tokens in a text.
    
    This is a simple approximation based on the average ratio of tokens to characters.
    For more accurate counting, provider-specific tokenizers should be used.
    
    Args:
        text: The text to count tokens for
        
    Returns:
        The approximate number of tokens
    """
    # Simple approximation: 1 token ≈ 4 characters
    return len(text) // 4

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        The configuration as a dictionary
    """
    if not os.path.exists(config_path):
        logger.warning(f"Configuration file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config: The configuration dictionary
        config_path: Path to save the configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the truncated text
        suffix: Suffix to append to truncated text
        
    Returns:
        The truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (values override dict1)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def format_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception as a dictionary.
    
    Args:
        error: The exception to format
        
    Returns:
        A dictionary with error information
    """
    return {
        "error": str(error),
        "type": type(error).__name__,
        "timestamp": timestamp()
    }
