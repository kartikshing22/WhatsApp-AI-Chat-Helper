"""
Utility functions for WhatsApp AI Chat Helper.
Includes safety filtering, message formatting, and helper functions.
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SafetyFilter:
    """Safety filter to prevent explicit or abusive content."""
    
    # List of explicit/abusive keywords (can be expanded)
    BLOCKED_KEYWORDS = [
        # Add your blocked keywords here
    ]
    
    # Patterns for detecting potentially harmful content
    HARMFUL_PATTERNS = [
        r'\b(hate|kill|die|suicide)\b',  # Example patterns
    ]
    
    @classmethod
    def is_safe(cls, text: str) -> bool:
        """
        Check if text is safe to send.
        
        Args:
            text: Text to check
            
        Returns:
            True if safe, False otherwise
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check blocked keywords
        for keyword in cls.BLOCKED_KEYWORDS:
            if keyword.lower() in text_lower:
                logger.warning(f"Blocked keyword detected: {keyword}")
                return False
        
        # Check harmful patterns
        for pattern in cls.HARMFUL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Harmful pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def filter_response(cls, response: str) -> Optional[str]:
        """
        Filter and clean response text.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Filtered response or None if unsafe
        """
        if not response:
            return None
        
        # Strip whitespace
        response = response.strip()
        
        # Remove common LLM artifacts
        response = re.sub(r'^["\']|["\']$', '', response)  # Remove quotes
        response = re.sub(r'\n{3,}', '\n\n', response)  # Limit newlines
        
        # Check safety
        if not cls.is_safe(response):
            logger.warning("Response failed safety check")
            return None
        
        return response


def format_messages_for_llm(messages: List[Dict[str, str]]) -> str:
    """
    Format chat messages for LLM input.
    
    Args:
        messages: List of message dicts with 'text', 'sender', 'timestamp' keys
        
    Returns:
        Formatted string for LLM
    """
    formatted = []
    
    for msg in messages:
        sender = msg.get('sender', 'Unknown')
        text = msg.get('text', '')
        timestamp = msg.get('timestamp', '')
        
        # Format: [Sender] (timestamp): message
        if timestamp:
            formatted.append(f"[{sender}] ({timestamp}): {text}")
        else:
            formatted.append(f"[{sender}]: {text}")
    
    return "\n".join(formatted)


def parse_message_element(element) -> Optional[Dict[str, str]]:
    """
    Parse a message element from WhatsApp Web DOM.
    
    Args:
        element: Playwright element handle
        
    Returns:
        Dict with 'text', 'sender', 'timestamp', 'direction' or None
    """
    try:
        # Get message text
        text_elem = element.query_selector('[data-testid="msg-container"] span.selectable-text')
        if not text_elem:
            return None
        
        text = text_elem.inner_text().strip()
        if not text:
            return None
        
        # Determine direction (incoming vs outgoing)
        # Outgoing messages have specific attributes
        is_outgoing = element.get_attribute("data-id") and "true" in str(element.get_attribute("data-id"))
        
        # Try to get sender name (for group chats)
        sender_elem = element.query_selector('[data-testid="conversation-header"] span, span[data-testid="conversation-header"]')
        sender = "You" if is_outgoing else "Contact"
        
        # Try to get timestamp
        time_elem = element.query_selector('span[data-testid="msg-meta"]')
        timestamp = time_elem.inner_text().strip() if time_elem else ""
        
        return {
            'text': text,
            'sender': sender,
            'timestamp': timestamp,
            'direction': 'outgoing' if is_outgoing else 'incoming'
        }
    except Exception as e:
        logger.error(f"Error parsing message element: {e}")
        return None


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

