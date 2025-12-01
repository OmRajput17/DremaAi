"""
Flask Chunk Retrieval API Application
Main application file using modularized structure
"""
import os
from flask import Flask
from flask_cors import CORS  # 👈 add this

from src.config import Config
from src.components import EducationContentFetcher, ContentProcessor
from src.routes import Routes
from src.logging import get_logger
from src.utils.vector_cache import VectorStoreCache

logger = get_logger(__name__)

def create_app():
    logger.info("=" * 70)
    logger.info("Starting Flask Chunk Retrieval API Application")
    logger.info("=" * 70)

    app = Flask(__name__)

    # ✅ Enable CORS BEFORE registering routes
    # Allow your Vite dev server origin:
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False,  # you are just using fetch, no cookies => False is fine
    )

    config = Config()
    embeddings = config.initialize_embeddings()

    logger.info("Initializing vector store cache...")
    vector_cache = VectorStoreCache(cache_dir="cache/vector_stores")

    logger.info("Initializing application components...")
    fetcher = EducationContentFetcher()
    content_processor = ContentProcessor(embeddings, vector_cache=vector_cache)

    logger.info("Registering routes...")
    Routes(app, fetcher, content_processor)

    logger.info("Application initialization complete!")
    logger.info("=" * 70)

    return app

# created once, for gunicorn
app = create_app()

if __name__ == '__main__':
    # LOCAL DEV ONLY
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask development server on http://localhost:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
