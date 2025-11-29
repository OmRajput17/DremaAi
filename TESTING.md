# Local Testing Guide - Drema AI Chunk Retrieval API

This guide provides comprehensive instructions for testing the Flask Chunk Retrieval API locally.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Starting the Application](#starting-the-application)
- [Testing the API](#testing-the-api)
- [Troubleshooting](#troubleshooting)
- [Advanced Testing](#advanced-testing)

---

## Prerequisites

Before you start testing, ensure you have:

- **Python 3.8+** installed
- **pip** package manager
- **API Keys** for:
  - OpenAI API (for embeddings)
  - Groq API (optional, if using LLM features)
  - LangChain API (optional, for tracing)

---

## Initial Setup

### 1. Navigate to Project Directory

```bash
cd "d:\Drema Ai"
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (if not already present):

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for LangChain tracing)
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_PROJECT=drema-ai-chunk-retrieval

# Optional (if using Groq)
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
```

> **⚠️ IMPORTANT**: The `OPENAI_API_KEY` is **required** for the application to work, as it uses OpenAI embeddings for vector similarity search.

### 5. Verify Data Files Exist

Ensure the following files/directories exist:
- ✅ `category.json` - Contains board/class/subject hierarchy
- ✅ `topics.json` - Contains topic mappings
- ✅ `data/` - Directory with educational content text files

---

## Starting the Application

### Method 1: Using main.py (Recommended for Testing)

```bash
python main.py
```

The server will start on **http://localhost:8080**

### Method 2: Using Flask directly

```bash
flask --app main run --port 8080 --debug
```

### Method 3: Using Gunicorn (Production-like)

```bash
gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app
```

> **📝 Note**: The application uses port **8080** by default (not 5000 like mentioned in the old README).

### Verify Application Started

You should see logs like:

```
======================================================================
Starting Flask Chunk Retrieval API Application
======================================================================
Initializing Flask application...
Initializing vector store cache...
Initializing application components...
Registering routes...
Application initialization complete!
======================================================================
Starting Flask development server on http://localhost:8080
```

---

## Testing the API

The API provides 5 main endpoints. Test them in the order below:

### 1. Test Health/Boards Endpoint

#### **GET** `/api/boards`

Retrieves all available educational boards (CBSE, ICSE, etc.)

**Using curl:**
```bash
curl http://localhost:8080/api/boards
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/boards" -Method Get | ConvertTo-Json
```

**Expected Response:**
```json
{
  "success": true,
  "boards": ["CBSE", "ICSE", "IB", "State Board"]
}
```

---

### 2. Test Classes Endpoint

#### **GET** `/api/classes/<board>`

Retrieves classes for a specific board.

**Example:**
```bash
curl http://localhost:8080/api/classes/CBSE
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/classes/CBSE" -Method Get | ConvertTo-Json
```

**Expected Response:**
```json
{
  "success": true,
  "board": "CBSE",
  "classes": ["9", "10", "11", "12"]
}
```

---

### 3. Test Subjects Endpoint

#### **GET** `/api/subjects/<board>/<class_num>`

Retrieves subjects for a specific board and class.

**Example:**
```bash
curl http://localhost:8080/api/subjects/CBSE/11
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/subjects/CBSE/11" -Method Get | ConvertTo-Json
```

**Expected Response:**
```json
{
  "success": true,
  "board": "CBSE",
  "class": "11",
  "subjects": ["Physics", "Chemistry", "Mathematics", "Biology"]
}
```

---

### 4. Test Topics Endpoint

#### **GET** `/api/topics/<board>/<class_num>/<subject>`

Retrieves topics for a specific board, class, and subject.

**Example:**
```bash
curl http://localhost:8080/api/topics/CBSE/11/Physics
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/topics/CBSE/11/Physics" -Method Get | ConvertTo-Json
```

**Expected Response:**
```json
{
  "success": true,
  "board": "CBSE",
  "class": "11",
  "subject": "Physics",
  "topics": [
    {"id": "1", "name": "Mechanics"},
    {"id": "2", "name": "Thermodynamics"},
    ...
  ]
}
```

---

### 5. Test Chunk Retrieval Endpoint (Main Feature)

#### **POST** `/api/retrieve_chunks`

Retrieves content chunks based on specified parameters.

**Request Body Schema:**
```json
{
  "board": "string (required)",
  "class": "string (required)",
  "subject": "string (required)",
  "topics": ["array of topic IDs (required)"],
  "num_chunks": "integer (optional, default: 10)",
  "difficulty": "string (optional: easy/medium/hard, default: medium)"
}
```

**Example Request (curl):**
```bash
curl -X POST http://localhost:8080/api/retrieve_chunks \
  -H "Content-Type: application/json" \
  -d "{\"board\":\"CBSE\",\"class\":\"11\",\"subject\":\"Physics\",\"topics\":[\"1\"],\"num_chunks\":5,\"difficulty\":\"medium\"}"
```

**PowerShell:**
```powershell
$body = @{
    board = "CBSE"
    class = "11"
    subject = "Physics"
    topics = @("1")
    num_chunks = 5
    difficulty = "medium"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/retrieve_chunks" `
    -Method Post `
    -Body $body `
    -ContentType "application/json" | ConvertTo-Json -Depth 10
```

**Expected Response:**
```json
{
  "success": true,
  "metadata": {
    "board": "CBSE",
    "class": "11",
    "subject": "Physics",
    "topics_requested": 1,
    "difficulty": "medium",
    "total_chunks": 5
  },
  "topic_info": [
    {
      "topic_num": "1",
      "topic_name": "Mechanics",
      "book_name": "Physics Textbook",
      "chunks_retrieved": 5
    }
  ],
  "chunks": [
    {
      "content": "Chunk content here...",
      "chunk_index": 0,
      "relevance_rank": 1,
      "topic_num": "1",
      "topic_name": "Mechanics"
    },
    ...
  ]
}
```

---

## Testing with Postman

### Import Collection

1. Open **Postman**
2. Create a new collection named "Drema AI API"
3. Add the following requests:

#### Request 1: Get Boards
- **Method**: GET
- **URL**: `http://localhost:8080/api/boards`

#### Request 2: Get Classes
- **Method**: GET
- **URL**: `http://localhost:8080/api/classes/CBSE`

#### Request 3: Get Subjects
- **Method**: GET
- **URL**: `http://localhost:8080/api/subjects/CBSE/11`

#### Request 4: Get Topics
- **Method**: GET
- **URL**: `http://localhost:8080/api/topics/CBSE/11/Physics`

#### Request 5: Retrieve Chunks
- **Method**: POST
- **URL**: `http://localhost:8080/api/retrieve_chunks`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "board": "CBSE",
  "class": "11",
  "subject": "Physics",
  "topics": ["1", "2"],
  "num_chunks": 10,
  "difficulty": "hard"
}
```

---

## Testing with Python Script

Create a test script `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8080"

def test_boards():
    print("Testing GET /api/boards...")
    response = requests.get(f"{BASE_URL}/api/boards")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_classes():
    print("Testing GET /api/classes/CBSE...")
    response = requests.get(f"{BASE_URL}/api/classes/CBSE")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_subjects():
    print("Testing GET /api/subjects/CBSE/11...")
    response = requests.get(f"{BASE_URL}/api/subjects/CBSE/11")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_topics():
    print("Testing GET /api/topics/CBSE/11/Physics...")
    response = requests.get(f"{BASE_URL}/api/topics/CBSE/11/Physics")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

def test_retrieve_chunks():
    print("Testing POST /api/retrieve_chunks...")
    payload = {
        "board": "CBSE",
        "class": "11",
        "subject": "Physics",
        "topics": ["1"],
        "num_chunks": 3,
        "difficulty": "easy"
    }
    response = requests.post(
        f"{BASE_URL}/api/retrieve_chunks",
        json=payload
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("\n")

if __name__ == "__main__":
    print("="*60)
    print("Drema AI API Testing")
    print("="*60 + "\n")
    
    test_boards()
    test_classes()
    test_subjects()
    test_topics()
    test_retrieve_chunks()
    
    print("="*60)
    print("All tests completed!")
    print("="*60)
```

**Run the test:**
```bash
# First install requests if not already
pip install requests

# Run the test script
python test_api.py
```

---

## Troubleshooting

### Issue: Port 8080 already in use

**Solution 1**: Change port in `main.py`:
```python
app.run(debug=True, port=5001)  # Use any available port
```

**Solution 2**: Kill the process using port 8080:
```powershell
# Find process
netstat -ano | findstr :8080

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

---

### Issue: `OPENAI_API_KEY not found`

**Error Message:**
```
ValueError: OPENAI_API_KEY is required but not set
```

**Solution:**
1. Verify `.env` file exists in project root
2. Check `.env` contains: `OPENAI_API_KEY=sk-...`
3. Restart the application after adding the key

---

### Issue: Module Not Found Errors

**Solution:**
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

### Issue: No chunks retrieved

**Possible Causes:**
1. Topic ID doesn't exist in `topics.json`
2. Content file is missing in `data/` directory
3. Content file is empty or malformed

**Solutions:**
- Check `topics.json` for valid topic IDs
- Verify corresponding text file exists in `data/`
- Check logs directory for detailed error messages

---

### Issue: Vector cache errors

**Solution:**
```bash
# Clear vector cache
Remove-Item -Recurse -Force cache\vector_stores\*

# Restart application
python main.py
```

---

## Advanced Testing

### Testing with Multiple Topics

```bash
curl -X POST http://localhost:8080/api/retrieve_chunks \
  -H "Content-Type: application/json" \
  -d "{\"board\":\"CBSE\",\"class\":\"11\",\"subject\":\"Physics\",\"topics\":[\"1\",\"2\",\"3\"],\"num_chunks\":15,\"difficulty\":\"hard\"}"
```

### Testing Difficulty Levels

Test each difficulty level:

**Easy:**
```json
{"difficulty": "easy", ...}
```

**Medium:**
```json
{"difficulty": "medium", ...}
```

**Hard:**
```json
{"difficulty": "hard", ...}
```

### Load Testing

Using Apache Bench (if installed):
```bash
ab -n 100 -c 10 http://localhost:8080/api/boards
```

Using Python:
```python
import concurrent.futures
import requests

def make_request(i):
    response = requests.get("http://localhost:8080/api/boards")
    return response.status_code

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(make_request, range(100)))
    
print(f"Success rate: {results.count(200)/len(results)*100}%")
```

---

## Monitoring Logs

Logs are stored in the `logs/` directory. Monitor them in real-time:

**PowerShell:**
```powershell
Get-Content logs\app.log -Wait -Tail 50
```

**Command Prompt:**
```cmd
tail -f logs\app.log
```

---

## Checking Vector Store Cache

The application caches vector embeddings for performance:

**Cache Location:** `cache/vector_stores/`

**View Cache:**
```powershell
Get-ChildItem cache\vector_stores\ -Recurse
```

**Clear Cache** (if needed):
```powershell
Remove-Item cache\vector_stores\* -Recurse -Force
```

---

## Testing Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured with valid API keys
- [ ] Application starts without errors
- [ ] GET `/api/boards` returns boards
- [ ] GET `/api/classes/<board>` returns classes
- [ ] GET `/api/subjects/<board>/<class>` returns subjects
- [ ] GET `/api/topics/<board>/<class>/<subject>` returns topics
- [ ] POST `/api/retrieve_chunks` returns chunks successfully
- [ ] Logs are being generated in `logs/` directory
- [ ] Vector cache is being created in `cache/vector_stores/`
- [ ] Different difficulty levels work correctly
- [ ] Multiple topics can be processed simultaneously

---

## Quick Testing Commands (Copy-Paste Ready)

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Start the application
python main.py

# 3. In a new terminal, test the API
# Get boards
Invoke-RestMethod -Uri "http://localhost:8080/api/boards" -Method Get | ConvertTo-Json

# Get classes
Invoke-RestMethod -Uri "http://localhost:8080/api/classes/CBSE" -Method Get | ConvertTo-Json

# Get subjects
Invoke-RestMethod -Uri "http://localhost:8080/api/subjects/CBSE/11" -Method Get | ConvertTo-Json

# Get topics
Invoke-RestMethod -Uri "http://localhost:8080/api/topics/CBSE/11/Physics" -Method Get | ConvertTo-Json

# Retrieve chunks
$body = @{
    board = "CBSE"
    class = "11"
    subject = "Physics"
    topics = @("1")
    num_chunks = 5
    difficulty = "medium"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/retrieve_chunks" -Method Post -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 10
```

---

## Additional Resources

- **Main Application**: `main.py`
- **Routes Definition**: `src/routes.py`
- **Configuration**: `src/config.py`
- **Logs Directory**: `logs/`
- **Data Files**: `data/`
- **Environment Variables**: `.env`

---

## Support

If you encounter issues during testing:

1. **Check logs** in `logs/` directory
2. **Verify API keys** in `.env` file
3. **Ensure data files exist** (`category.json`, `topics.json`, `data/`)
4. **Check Python version**: Must be 3.8+
5. **Review application startup logs** for initialization errors

---

**Last Updated**: November 2025
**Application Version**: Chunk Retrieval API v1.0
**Default Port**: 8080
