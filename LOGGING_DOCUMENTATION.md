# Logging System Documentation

## Overview
A comprehensive logging system has been integrated into the Flask MCQ Generator application. The logging system provides detailed tracking of application flow, debugging information, and error handling across all modules.

## Logging Features

### 1. **Multi-Level Logging**
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages about application flow
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems

### 2. **Dual Output**
- **Console Output**: Real-time logs displayed in the terminal (INFO level and above)
- **File Output**: Detailed logs saved to files (DEBUG level and above)

### 3. **Log Rotation**
- Automatic file rotation when log file reaches 10MB
- Keeps 5 backup files
- Daily log files with date in filename: `drema_ai_YYYYMMDD.log`

### 4. **Structured Format**
```
YYYY-MM-DD HH:MM:SS - module.name - LEVEL - [filename.py:line] - message
```

Example:
```
2025-11-24 12:06:56 - src.config - INFO - [config.py:20] - Initializing application configuration...
```

## Log File Location

Logs are stored in: `d:\Drema Ai\logs\`

Current log file: `drema_ai_20251124.log`

## Logging Implementation

### Module: `src/logging/logger.py`

```python
class LoggerSetup:
    """Setup and configure application logging."""
    
    def __init__(self, app_name="drema_ai", log_dir="logs"):
        # Creates logs directory
        # Sets up log file naming with date
    
    def get_logger(self, name):
        # Returns configured logger instance
        # Adds file and console handlers
        # Sets formatters
```

### Usage in Code

```python
from src.logging import get_logger

logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

## Logging Coverage

### 1. **Application Startup** (`app.py`)
```
12:06:56 - INFO - Starting Flask MCQ Generator Application
12:06:56 - INFO - Initializing Flask application...
12:06:57 - INFO - Initializing application components...
12:06:57 - INFO - Registering routes...
12:06:57 - INFO - Application initialization complete!
12:06:57 - INFO - Starting Flask development server on http://localhost:5000
```

### 2. **Configuration** (`src/config.py`)
```
12:06:56 - INFO - Initializing application configuration...
12:06:56 - DEBUG - Environment variables loaded
12:06:56 - DEBUG - Environment variables configured
12:06:56 - INFO - Configuration initialized successfully
12:06:56 - INFO - Initializing LLM with model: llama-3.1-70b-versatile, temperature: 0
12:06:57 - INFO - LLM initialized successfully
```

### 3. **Content Fetcher** (`src/components/content_fetcher.py`)
```
12:06:57 - INFO - Initializing EducationContentFetcher...
12:06:57 - DEBUG - Loading category file: category.json
12:06:57 - DEBUG - Loading topics file: topics.json
12:06:57 - INFO - EducationContentFetcher initialized successfully
12:09:48 - INFO - Fetching content for: Board=CBSE, Class=11, Subject=Physics, Topic=4
12:09:48 - DEBUG - Topic name found: Laws of Motion
12:09:48 - INFO - Searching in 2 book(s)...
12:09:48 - DEBUG - Checking book: Physics Part-I (ID: ke11101)
12:09:48 - INFO - Topic found in book: Physics Part-I
```

### 4. **MCQ Generator** (`src/components/mcq_generator.py`)
```
12:15:30 - INFO - Generating 5 MCQs at medium difficulty for topic: Laws of Motion
12:15:30 - DEBUG - Content length: 15234 characters
12:15:30 - INFO - Invoking LLM to generate MCQs...
12:15:45 - DEBUG - LLM response received
12:15:45 - INFO - Successfully generated 5 MCQs
```

### 5. **Routes** (`src/routes.py`)
```
12:09:35 - INFO - GET / - Rendering main page
12:09:35 - DEBUG - Found 19 boards
12:09:39 - INFO - GET /get_classes/CBSE
12:09:39 - DEBUG - Found 12 classes for board: CBSE
12:09:43 - INFO - GET /get_subjects/CBSE/11
12:09:43 - DEBUG - Found 19 subjects for CBSE class 11
12:09:48 - INFO - GET /get_topics/CBSE/11/Physics
12:09:48 - DEBUG - Retrieved topics for CBSE/11/Physics: 15 topics found
12:10:15 - INFO - POST /generate - MCQ generation request received
12:10:15 - DEBUG - Request data: {'board': 'CBSE', 'class': '11', ...}
12:10:30 - INFO - Successfully generated 5 MCQs
```

## Error Logging Examples

### Content Not Found
```
12:15:00 - WARNING - No books found for this subject in category.json
12:15:00 - WARNING - Topic 99 not found in any available books. Checked: ke11101, ke11102
```

### File Errors
```
12:15:05 - DEBUG - Book file not found: data/invalid_book.txt
12:15:05 - ERROR - Error reading book ke11103: [Errno 2] No such file or directory
```

### MCQ Generation Errors
```
12:16:00 - ERROR - Invalid difficulty level: super_hard
12:16:05 - ERROR - Error parsing MCQs: Expecting value: line 1 column 1 (char 0)
12:16:05 - DEBUG - Raw response: {malformed json...}
```

### Route Errors
```
12:16:10 - WARNING - Content fetch failed: Topic not found
12:16:15 - ERROR - MCQ generation failed
12:16:20 - ERROR - Error in generate endpoint: 'NoneType' object has no attribute 'get'
```

## Benefits of Logging System

### 1. **Debugging**
- Track exact flow of execution
- Identify where errors occur
- See variable values at different stages

### 2. **Monitoring**
- Monitor application health
- Track usage patterns
- Identify performance bottlenecks

### 3. **Audit Trail**
- Record all user actions
- Track API calls
- Maintain history of operations

### 4. **Error Diagnosis**
- Full stack traces in logs
- Context information
- Timestamp of issues

## Log Analysis Tips

### Find Errors
```bash
# Windows PowerShell
Select-String -Path "logs\drema_ai_*.log" -Pattern "ERROR"
```

### Track Specific Request
```bash
# Find all logs for a specific timestamp
Select-String -Path "logs\drema_ai_*.log" -Pattern "12:09:48"
```

### Count Log Levels
```bash
# Count INFO messages
(Select-String -Path "logs\drema_ai_*.log" -Pattern "INFO").Count
```

## Configuration Options

### Change Log Level
In `src/logging/logger.py`:
```python
# For more verbose logging
logger.setLevel(logging.DEBUG)

# For less verbose logging
logger.setLevel(logging.WARNING)
```

### Change Log File Size
```python
file_handler = RotatingFileHandler(
    self.log_path,
    maxBytes=20*1024*1024,  # 20MB instead of 10MB
    backupCount=10,         # Keep 10 backups instead of 5
    encoding='utf-8'
)
```

### Change Log Format
```python
detailed_formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

## Best Practices

### 1. **Use Appropriate Log Levels**
- DEBUG: Variable values, detailed flow
- INFO: Major milestones, successful operations
- WARNING: Recoverable issues, missing optional data
- ERROR: Failures, exceptions

### 2. **Include Context**
```python
logger.info(f"Fetching content for: Board={board}, Class={class_num}")
```

### 3. **Log Exceptions with Stack Trace**
```python
try:
    # code
except Exception as e:
    logger.error(f"Error: {str(e)}", exc_info=True)
```

### 4. **Don't Log Sensitive Data**
```python
# Bad
logger.debug(f"API Key: {api_key}")

# Good
logger.debug("API Key configured")
```

## Troubleshooting

### Logs Not Appearing
1. Check if `logs/` directory exists
2. Verify file permissions
3. Check log level settings

### Log Files Too Large
1. Reduce log level (INFO instead of DEBUG)
2. Decrease maxBytes in RotatingFileHandler
3. Reduce backupCount

### Performance Impact
- Logging has minimal performance impact
- File I/O is buffered
- Console output is async

## Summary

The logging system provides:
- ✅ Comprehensive tracking across all modules
- ✅ File and console output
- ✅ Automatic log rotation
- ✅ Structured, searchable format
- ✅ Multiple log levels
- ✅ Easy debugging and monitoring
- ✅ Production-ready configuration

All application activities are now logged, making it easy to debug issues, monitor performance, and maintain an audit trail!
