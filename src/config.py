"""
Configuration Module
Handles environment variables and embeddings initialization
"""
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
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
        os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", '')
        logger.debug("Environment variables configured")
        
        # Initialize embeddings
        self.embeddings = None
        logger.info("Configuration initialized successfully")
    
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
    
    def get_embeddings(self):
        """Get or initialize embeddings."""
        if not self.embeddings:
            return self.initialize_embeddings()
        return self.embeddings
