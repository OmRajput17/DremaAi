# Modular Flask Application Structure

## Overview
The Flask application has been refactored into a clean, modular structure following best practices for maintainability and scalability.

## Directory Structure

```
Drema Ai/
├── app.py                          # Main application entry point
├── templates/
│   └── index.html                  # Frontend template
├── src/                            # Source code package
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Configuration and model initialization
│   ├── routes.py                   # Flask route definitions
│   ├── components/                 # Core components
│   │   ├── __init__.py
│   │   ├── content_fetcher.py     # Educational content fetching
│   │   ├── mcq_generator.py       # MCQ generation logic
│   │   └── loader.py              # (Reserved for future use)
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── common.py              # Common utilities
│   │   └── caching.py             # (Reserved for caching)
│   └── logging/                    # Logging utilities
│       └── (Reserved for logging)
├── category.json                   # Board/class/subject data
├── topics.json                     # Topic mappings
├── data/                           # Educational content files
├── requirements.txt                # Python dependencies
└── .env                           # Environment variables
```

## Module Breakdown

### 1. `app.py` - Application Entry Point
**Purpose**: Main application file with factory pattern

**Key Features**:
- Application factory function `create_app()`
- Clean initialization flow
- Easy to test and extend

**Code Structure**:
```python
def create_app():
    app = Flask(__name__)
    config = Config()
    llm = config.initialize_llm()
    fetcher = EducationContentFetcher()
    mcq_generator = MCQGenerator(llm)
    Routes(app, fetcher, mcq_generator)
    return app
```

### 2. `src/config.py` - Configuration Module
**Purpose**: Centralized configuration and model initialization

**Responsibilities**:
- Load environment variables
- Initialize LLM (Language Model)
- Initialize embeddings
- Provide singleton access to models

**Key Methods**:
- `initialize_llm()` - Set up Groq LLM
- `initialize_embeddings()` - Set up HuggingFace embeddings
- `get_llm()` - Get or create LLM instance
- `get_embeddings()` - Get or create embeddings instance

### 3. `src/routes.py` - Routes Module
**Purpose**: Handle all Flask route definitions

**Responsibilities**:
- Define all API endpoints
- Handle request/response logic
- Coordinate between components

**Endpoints**:
- `GET /` - Main page
- `GET /get_classes/<board>` - Get classes for board
- `GET /get_subjects/<board>/<class>` - Get subjects
- `GET /get_topics/<board>/<class>/<subject>` - Get topics
- `POST /generate` - Generate MCQs

### 4. `src/components/content_fetcher.py` - Content Fetcher
**Purpose**: Fetch educational content from data files

**Responsibilities**:
- Load category and topic data
- Navigate board/class/subject hierarchy
- Extract topic content from books
- Handle file operations

**Key Methods**:
- `get_boards()` - List all boards
- `get_classes(board)` - Get classes for board
- `get_subjects(board, class)` - Get subjects
- `get_topics(board, class, subject)` - Get topics
- `fetch_content(...)` - Fetch topic content

### 5. `src/components/mcq_generator.py` - MCQ Generator
**Purpose**: Generate MCQs using LLM

**Responsibilities**:
- Create prompts for LLM
- Handle different difficulty levels
- Parse LLM responses
- Validate MCQ format

**Key Methods**:
- `generate_mcqs(num, difficulty, topic, content)` - Generate MCQs

**Difficulty Levels**:
- **Easy**: Basic recall and definitions
- **Medium**: Comprehension and application
- **Hard**: Analysis and critical thinking

### 6. `src/utils/common.py` - Utility Functions
**Purpose**: Reusable utility functions

**Functions**:
- `validate_difficulty_level(difficulty)` - Validate difficulty input
- `validate_num_questions(num)` - Validate question count
- `format_topic_name(num, name)` - Format topic display
- `clean_json_response(text)` - Clean LLM JSON output

## Benefits of Modular Structure

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Easy to understand what each file does
- Changes in one module don't affect others

### 2. **Maintainability**
- Easy to locate and fix bugs
- Clear organization makes updates simple
- New developers can understand quickly

### 3. **Testability**
- Each component can be tested independently
- Mock dependencies easily
- Unit tests are straightforward

### 4. **Scalability**
- Easy to add new features
- Can extend without modifying existing code
- Clear patterns to follow

### 5. **Reusability**
- Components can be used in other projects
- Utility functions are standalone
- Models can be shared across routes

## How to Use

### Running the Application
```bash
python app.py
```

### Importing Components
```python
from src.components import EducationContentFetcher, MCQGenerator
from src.config import Config
from src.utils import validate_difficulty_level

# Use components
config = Config()
llm = config.get_llm()
fetcher = EducationContentFetcher()
generator = MCQGenerator(llm)
```

### Adding New Routes
1. Open `src/routes.py`
2. Add new method to `Routes` class
3. Register in `register_routes()` method

Example:
```python
def new_endpoint(self):
    # Your logic here
    return jsonify({'status': 'success'})

# In register_routes():
self.app.add_url_rule('/new', 'new', self.new_endpoint)
```

### Adding New Components
1. Create new file in `src/components/`
2. Define your class
3. Export in `src/components/__init__.py`
4. Import in `app.py` and use

## Testing Strategy

### Unit Tests
Test individual components:
```python
# Test content fetcher
def test_get_boards():
    fetcher = EducationContentFetcher()
    boards = fetcher.get_boards()
    assert len(boards) > 0

# Test MCQ generator
def test_generate_mcqs():
    llm = ChatGroq(...)
    generator = MCQGenerator(llm)
    mcqs = generator.generate_mcqs(5, 'easy', 'Topic', 'Content')
    assert len(mcqs) == 5
```

### Integration Tests
Test routes and full flow:
```python
def test_generate_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.post('/generate', json={...})
    assert response.status_code == 200
```

## Future Enhancements

### Planned Additions
1. **Caching** (`src/utils/caching.py`)
   - Cache LLM responses
   - Cache content fetches
   - Reduce API calls

2. **Logging** (`src/logging/`)
   - Request logging
   - Error tracking
   - Performance monitoring

3. **Database** (`src/database/`)
   - Store generated MCQs
   - User management
   - Analytics

4. **Authentication** (`src/auth/`)
   - User login
   - API key management
   - Rate limiting

## Best Practices

### Code Organization
- ✅ One class per file
- ✅ Related functions grouped together
- ✅ Clear naming conventions
- ✅ Proper documentation

### Error Handling
- ✅ Try-except blocks in critical sections
- ✅ Meaningful error messages
- ✅ Proper HTTP status codes
- ✅ Logging errors

### Configuration
- ✅ Environment variables for secrets
- ✅ Centralized config management
- ✅ Default values provided
- ✅ Easy to override

## Troubleshooting

### Import Errors
If you get import errors, ensure:
1. You're in the project root directory
2. `src/__init__.py` exists
3. Python can find the `src` package

### Module Not Found
Run from project root:
```bash
cd "d:\Drema Ai"
python app.py
```

### Configuration Issues
Check:
1. `.env` file exists
2. All required keys are set
3. API keys are valid

## Summary

The modularized structure provides:
- 🎯 Clear separation of concerns
- 📦 Reusable components
- 🧪 Easy testing
- 📈 Scalable architecture
- 🔧 Simple maintenance
- 📚 Better documentation

This structure follows Flask best practices and makes the application production-ready!
