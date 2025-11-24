"""
Configuration Module
Handles environment variables and model initialization
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from src.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


class Config:
    """Application configuration and model initialization."""
    
    def __init__(self):
        """Load environment variables and initialize models."""
        logger.info("Initializing application configuration...")
        
        # Load environment variables
        load_dotenv()
        logger.debug("Environment variables loaded")
        
        # Set environment variables
        os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY', '')
        os.environ["LANGCHAIN_TRACING_V2"] = 'true'
        os.environ['LANGCHAIN_PROJECT'] = os.getenv('LANGCHAIN_PROJECT', 'drema-ai')
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", '')
        os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", '')
        logger.debug("Environment variables configured")
        
        # Initialize models
        self.llm = None
        self.embeddings = None
        logger.info("Configuration initialized successfully")
        
    def initialize_llm(self, model="llama-3.3-70b-versatile", temperature=0):
        """
        Initialize the language model.
        
        Args:
            model (str): Model name
            temperature (float): Temperature for generation
         
        Returns:
            ChatGroq: Initialized LLM instance
        """
        if not self.llm:
            logger.info(f"Initializing LLM with model: {model}, temperature: {temperature}")
            self.llm = ChatGroq(model=model, temperature=temperature)
            logger.info("LLM initialized successfully")
        return self.llm
    
    def initialize_embeddings(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embeddings model.
        
        Args:
            model_name (str): HuggingFace model name
        
        Returns:
            HuggingFaceEmbeddings: Initialized embeddings instance
        """
        if not self.embeddings:
            logger.info(f"Initializing embeddings with model: {model_name}")
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
            logger.info("Embeddings initialized successfully")
        return self.embeddings
    
    def get_llm(self):
        """Get or initialize LLM."""
        if not self.llm:
            return self.initialize_llm()
        return self.llm
    
    def get_embeddings(self):
        """Get or initialize embeddings."""
        if not self.embeddings:
            return self.initialize_embeddings()
        return self.embeddings
