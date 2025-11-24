"""
Flask MCQ Generator Application
Main application file using modularized structure
"""
from flask import Flask
from src.config import Config
from src.components import EducationContentFetcher, MCQGenerator
from src.routes import Routes
from src.logging import get_logger

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
    
    # Initialize configuration and models
    config = Config()
    llm = config.initialize_llm()
    
    # Initialize components
    logger.info("Initializing application components...")
    fetcher = EducationContentFetcher()
    mcq_generator = MCQGenerator(llm)
    
    # Register routes
    logger.info("Registering routes...")
    Routes(app, fetcher, mcq_generator)
    
    logger.info("Application initialization complete!")
    logger.info("=" * 70)
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask development server on http://localhost:5000")
    app.run(debug=True, port=5000)
