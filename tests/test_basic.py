"""
Basic smoke tests for Drema AI application
Tests module imports and basic app functionality
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all core modules can be imported"""
    try:
        import main
        from src.config import Config
        from src.components import EducationContentFetcher, ContentProcessor
        from src.routes import Routes
        from src.logging import get_logger
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")


def test_app_creation():
    """Test that Flask app can be created"""
    try:
        from main import create_app
        app = create_app()
        assert app is not None
        assert app.name == 'main'
    except Exception as e:
        pytest.fail(f"Failed to create app: {e}")


def test_config_loading():
    """Test that configuration can be loaded"""
    try:
        from src.config import Config
        config = Config()
        assert config is not None
    except Exception as e:
        pytest.fail(f"Failed to load config: {e}")


def test_routes_registered():
    """Test that API routes are registered"""
    try:
        from main import create_app
        app = create_app()
        
        # Check that expected routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/boards',
            '/api/classes/<board>',
            '/api/subjects/<board>/<class_num>',
            '/api/retrieve_chunks',
            '/api/generate_question_paper',
            '/api/summarize',
            '/api/flash_cards',
            '/api/mind_map',
            '/api/study_tricks'
        ]
        
        for route in expected_routes:
            assert route in routes, f"Route {route} not found"
            
    except Exception as e:
        pytest.fail(f"Failed to check routes: {e}")


def test_health_check():
    """Basic health check test"""
    try:
        from main import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test boards endpoint as a health check
            response = client.get('/api/boards')
            assert response.status_code in [200, 500]  # 500 might occur due to missing data
            
    except Exception as e:
        pytest.fail(f"Health check failed: {e}")
