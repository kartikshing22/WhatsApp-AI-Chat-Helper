"""
LLM Pipeline for WhatsApp AI Chat Helper.
Handles LangChain integration and response generation.
"""

import logging
from typing import List, Dict, Optional

# Try newer LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import LLMChain

from app.config import Config
from app.utils import SafetyFilter, format_messages_for_llm, truncate_text

logger = logging.getLogger(__name__)


class LLMPipeline:
    """LLM Pipeline for generating WhatsApp replies."""
    
    def __init__(self):
        """Initialize LLM pipeline with configured provider."""
        self.llm = self._create_llm()
        self.safety_filter = SafetyFilter()
        self.agent_type = "default"
        # self._setup_prompt_template()
        self.set_agent_type("default")
    
    def _create_llm(self):
        """Create LLM instance based on configured provider."""
        provider = Config.LLM_PROVIDER.lower()
        
        if provider == "openai":
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            logger.info(f"Using OpenAI model: {Config.OPENAI_MODEL}")
            try:
                return ChatOpenAI(
                    model=Config.OPENAI_MODEL,
                    temperature=0.7,
                    max_tokens=Config.MAX_RESPONSE_LENGTH
                )
            except TypeError:
                # Fallback for older API
                return ChatOpenAI(
                    model_name=Config.OPENAI_MODEL,
                    temperature=0.7,
                    max_tokens=Config.MAX_RESPONSE_LENGTH
                )
        
        
        elif provider == "gemini":
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            if ChatGoogleGenerativeAI is None:
                raise ValueError("ChatGoogleGenerativeAI not available. Install langchain-google-genai")
            logger.info(f"Using Gemini model: {Config.GEMINI_MODEL}")
            return ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL,
                temperature=0.7,
                # max_output_tokens=Config.MAX_RESPONSE_LENGTH
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    def set_agent_type(self, agent_type: str):
        """Set the agent type and update prompt template."""
        self.agent_type = agent_type
        self.setup_prompt_template()
    
    def setup_prompt_template(self):
        """Setup prompt template for generating replies."""
        if self.agent_type == "default":
            self.system_prompt = f"""You are a helpful AI assistant that generates natural, {Config.RESPONSE_TONE} WhatsApp messages.

            Guidelines:
            - Be natural, conversational, and contextually appropriate
            - Match the tone and style of the conversation
            - Keep responses concise (under {Config.MAX_RESPONSE_LENGTH} characters)
            - Be respectful and appropriate
            - Do not use explicit language or offensive content
            - Use hindi and english both language if the chat is in hindi
            - Do not use explicit emojis
            - Respond as if you are the person in the conversation

            Generate a single, natural reply based on the chat history provided."""
        elif self.agent_type == "friendly":
            self.system_prompt = f"""You are a AI assistant that generates Friendly Abusive,natural funny WhatsApp messages.

            Guidelines:
            - Use naughty,friendly,abusive friendly language and tone
            - Keep responses concise (under {Config.MAX_RESPONSE_LENGTH} characters)
           
            - use slang or colloquial expressions
            - Use hindi and english both language if the chat is in hindi
            - Do not use explicit emojis
            - Respond as if you are the person in the conversation

            Generate a single, reply based on the chat history provided."""
        elif self.agent_type == "flirty":
            self.system_prompt = f"""You are a AI assistant that generates Friendly ,naughty,romantic,vulagar,natural funny WhatsApp messages.

            Guidelines:
            - Use Friendly ,naughty,romantic,vulagar,natural language and tone
            - Keep responses concise (under {Config.MAX_RESPONSE_LENGTH} characters)
            - Use hindi and english both language if the chat is in hindi
            - Do not use explicit emojis
            - Respond as if you are the person in the conversation

            Generate a single, reply based on the chat history provided."""
        else:
            # Default fallback - handle directly to avoid recursion
            logger.warning(f"Unknown agent type: {self.agent_type}, using default")
            self.agent_type = "default"
            # Use default prompt
            self.system_prompt = f"""You are a helpful AI assistant that generates natural, {Config.RESPONSE_TONE} WhatsApp messages.

            Guidelines:
            - Be natural, conversational, and contextually appropriate
            - Match the tone and style of the conversation
            - Keep responses concise (under {Config.MAX_RESPONSE_LENGTH} characters)
            - Be respectful and appropriate
            - Do not use explicit language or offensive content
            - Use hindi and english both language if the chat is in hindi
            - Do not use explicit emojis
            - Respond as if you are the person in the conversation

            Generate a single, natural reply based on the chat history provided."""
        
        logger.info(f"Prompt template updated for agent type: {self.agent_type}")
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Chat History:\n{chat_history}\n\nGenerate a natural reply:"),
        ])
    
    def generate_reply(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Generate a reply based on chat history.
        
        Args:
            messages: List of message dicts with 'text', 'sender', 'timestamp'
            
        Returns:
            Generated reply text or None if generation fails
        """
        try:
            # Format messages for LLM
            chat_history = format_messages_for_llm(messages)
            
            if not chat_history:
                logger.warning("No chat history provided")
                return None
            
            logger.info(f"Generating reply based on {len(messages)} messages")
            
            # Create chain
            chain = self.prompt_template | self.llm | StrOutputParser()
            # chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
            
            # Generate response
            response = chain.invoke({"chat_history": chat_history})
            # response = chain.run(chat_history=chat_history)
            
            if not response:
                logger.warning("Empty response from LLM")
                return None
            
            # Clean and filter response
            response = response.strip()
            response = truncate_text(response, Config.MAX_RESPONSE_LENGTH)
            
            # Apply safety filter
            if Config.ENABLE_SAFETY_FILTER:
                response = self.safety_filter.filter_response(response)
                if not response:
                    logger.warning("Response filtered by safety check")
                    return None
            
            logger.info(f"Generated reply: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}", exc_info=True)
            return None
    
    def is_ready(self) -> bool:
        """Check if pipeline is ready to generate replies."""
        return self.llm is not None

