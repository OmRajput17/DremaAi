"""
Flask MCQ Generator Application
Main application file using modularized structure
"""
from flask import Flask
from src.config import Config
from src.components import EducationContentFetcher, MCQGenerator, ContentProcessor
from src.routes import Routes
from src.logging import get_logger
from src.utils.vector_cache import VectorStoreCache

# Initialize logger
logger = get_logger(__name__)


def create_app():
    """
    Application factory function.
    
    
    Returns:
        Flask: Configured Flask application
    """
    logger.info("=" * 70)
    logger.info("Starting Flask MCQ Generator Application")
    logger.info("=" * 70)
    
    # Initialize Flask app
    logger.info("Initializing Flask application...")
    app = Flask(__name__)
    
    # Set secret key for session management
    app.secret_key = 'drema-ai-mcq-generator-secret-key-2024'  # In production, use environment variable
    
    # Initialize configuration and models
    config = Config()
    llm = config.initialize_llm()
    embeddings = config.initialize_embeddings()
    
    # Initialize vector store cache
    logger.info("Initializing vector store cache...")
    vector_cache = VectorStoreCache(cache_dir="cache/vector_stores")
    
    # Initialize components
    logger.info("Initializing application components...")
    fetcher = EducationContentFetcher()
    content_processor = ContentProcessor(embeddings, vector_cache=vector_cache)
    mcq_generator = MCQGenerator(llm)
    
    # Register routes
    logger.info("Registering routes...")
    Routes(app, fetcher, mcq_generator, content_processor)
    
    logger.info("Application initialization complete!")
    logger.info("=" * 70)
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask development server on http://localhost:5000")
    app.run(debug=True, port=8080)
