"""
Configuration management for WhatsApp AI Chat Helper.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration class."""
    
    # LLM Provider Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # openai, claude, gemini
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Anthropic Claude Settings
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # Google Gemini Settings
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    
    # WhatsApp Web Settings
    WHATSAPP_WEB_URL = "https://web.whatsapp.com"
    BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))  # milliseconds
    
    # Session Persistence
    SESSION_DIR = Path(__file__).parent.parent / "session"
    SESSION_DIR.mkdir(exist_ok=True)
    
    # User Settings
    HUMAN_APPROVAL = os.getenv("HUMAN_APPROVAL", "true").lower() == "true"
    MAX_MESSAGES_TO_READ = int(os.getenv("MAX_MESSAGES_TO_READ", "30"))
    
    # AI Response Settings
    RESPONSE_TONE = os.getenv("RESPONSE_TONE", "romantic, respectful, natural")
    MAX_RESPONSE_LENGTH = int(os.getenv("MAX_RESPONSE_LENGTH", "500"))
    
    # Safety Settings
    ENABLE_SAFETY_FILTER = os.getenv("ENABLE_SAFETY_FILTER", "true").lower() == "true"
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = Path(__file__).parent.parent / "logs" / "app.log"
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []
        
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        elif cls.LLM_PROVIDER == "claude" and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when LLM_PROVIDER=claude")
        elif cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True

