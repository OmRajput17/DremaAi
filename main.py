"""
Flask Chunk Retrieval API Application
Main application file using modularized structure
"""
from flask import Flask
from src.config import Config
from src.components import EducationContentFetcher, ContentProcessor
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
    logger.info("Starting Flask Chunk Retrieval API Application")
    logger.info("=" * 70)
    
    # Initialize Flask app
    logger.info("Initializing Flask application...")
    app = Flask(__name__)
    
    # Initialize configuration and embeddings
    config = Config()
    embeddings = config.initialize_embeddings()
    
    # Initialize vector store cache
    logger.info("Initializing vector store cache...")
    vector_cache = VectorStoreCache(cache_dir="cache/vector_stores")
    
    # Initialize components
    logger.info("Initializing application components...")
    fetcher = EducationContentFetcher()
    content_processor = ContentProcessor(embeddings, vector_cache=vector_cache)
    
    # Register routes
    logger.info("Registering routes...")
    Routes(app, fetcher, content_processor)
    
    logger.info("Application initialization complete!")
    logger.info("=" * 70)
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask development server on http://localhost:8080")
    app.run(debug=True, port=8080)
