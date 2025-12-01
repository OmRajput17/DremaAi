"""
Configuration Module
Handles environment variables and embeddings initialization
"""
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from src.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class Config:
    """Application configuration and embeddings initialization."""
    
    def __init__(self):
        """Load environment variables and initialize configuration."""
        logger.info("Initializing application configuration...")
        
        # Load environment variables
        load_dotenv()
        logger.debug("Environment variables loaded")
        
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", '')
        logger.debug("Environment variables configured")
        
        # Initialize embeddings
        self.embeddings = None
        logger.info("Configuration initialized successfully")
    
    def initialize_embeddings(self, model_name="text-embedding-3-large"):
        """
        Initialize embeddings model.
        
        Args:
            model_name (str): OpenAI embeddings model name
                Options: 
                - "text-embedding-3-small" (recommended, cheap, 1536 dimensions)
                - "text-embedding-3-large" (best quality, 3072 dimensions)
                - "text-embedding-ada-002" (older, 1536 dimensions)
        
        Returns:
            OpenAIEmbeddings: Initialized embeddings instance
        """
        if not self.embeddings:
            logger.info(f"Initializing OpenAI embeddings with model: {model_name}")
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                logger.error("OPENAI_API_KEY not found in environment variables")
                raise ValueError("OPENAI_API_KEY is required but not set")
            
            self.embeddings = OpenAIEmbeddings(
                model=model_name,
                openai_api_key=api_key
            )
            logger.info("OpenAI embeddings initialized successfully")
        return self.embeddings
    
    def get_embeddings(self):
        """Get or initialize embeddings."""
        if not self.embeddings:
            return self.initialize_embeddings()
        return self.embeddings
    
    def initialize_llm(self, model_name="gpt-4o-mini"):
        """
        Initialize OpenAI LLM for question paper generation.
        
        Args:
            model_name (str): OpenAI model name
                Options:
                - "gpt-4o" (recommended, latest GPT-4 optimized)
                - "gpt-4o-mini" (faster, cheaper but may truncate)
                - "gpt-4-turbo"
        
        Returns:
            ChatOpenAI: Initialized LLM instance
        """
        logger.info(f"Initializing OpenAI LLM with model: {model_name}")
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY is required but not set")
        
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=0.7,  # Balanced creativity for question generation
            max_tokens=8000   # Increased for complete question papers
        )
        logger.info("OpenAI LLM initialized successfully")
        return llm