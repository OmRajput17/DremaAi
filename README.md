# MCQ Generator Flask App

![CI/CD Pipeline](https://github.com/OmRajput17/DremaAi/workflows/CI/CD%20Pipeline/badge.svg)
![Docker Build](https://github.com/OmRajput17/DremaAi/workflows/Docker%20Publish/badge.svg)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-drema--ai-blue)](https://hub.docker.com/r/YOUR_USERNAME/drema-ai)

A Flask web application that generates Multiple Choice Questions (MCQs) based on educational content from various boards, classes, subjects, and topics.

## Features

- 📚 Support for multiple educational boards (CBSE, ICSE, IB, etc.)
- 🎓 Dynamic selection of classes, subjects, and topics
- 🎯 Three difficulty levels: Easy, Medium, Hard
- 🤖 AI-powered MCQ generation using LangChain and OpenAI
- 💡 Clean and modern user interface
- ✅ Instant results with explanations
- 🚀 Automated CI/CD with GitHub Actions
- 🐳 Docker containerization for easy deployment


## Prerequisites

- Python 3.8 or higher
- API keys for:
  - OpenAI API (for embeddings and LLM inference)
  - LangChain/LangSmith (optional, for tracing)

## Installation

1. Clone the repository or navigate to the project directory:
```bash
cd "d:\Drema Ai"
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_PROJECT=DremaAI
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
PORT=5000
FLASK_ENV=production
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Select Board**: Choose from available educational boards (CBSE, ICSE, etc.)
2. **Select Class**: Pick the class/grade level
3. **Select Subject**: Choose the subject (Physics, Chemistry, Mathematics, etc.)
4. **Select Topic**: Pick a specific topic/chapter
5. **Number of Questions**: Enter how many MCQs you want (1-20)
6. **Difficulty Level**: Choose Easy, Medium, or Hard
7. Click **Generate MCQs** and wait for the AI to create your questions

## Project Structure

```
Drema Ai/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend HTML template
├── category.json         # Board/class/subject structure
├── topics.json          # Topic mappings
├── data/                # Text files with educational content
├── requirements.txt     # Python dependencies
└── .env                # Environment variables (create this)
```

## How It Works

1. **Content Fetching**: The app fetches educational content from text files based on your selection
2. **AI Processing**: Uses Groq's LLM (llama-3.1-70b-versatile) to generate contextual MCQs
3. **Smart Extraction**: Automatically extracts relevant topic content from books
4. **Dynamic UI**: Cascading dropdowns ensure you only see relevant options

## Features Explained

### Hardcoded Values Replaced
The original Jupyter notebook had these hardcoded values:
- `selected_board = "CBSE"`
- `selected_class = "11"`
- `selected_subject = "Physics"`
- `selected_topic = "4"`
- `num_question = 5`
- `difficulty_level = "hard"`

Now all these are **user inputs** through the web form!

### Difficulty Levels

- **Easy**: Tests basic recall and definitions
- **Medium**: Tests comprehension and application
- **Hard**: Tests analysis, synthesis, and critical thinking

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=True, port=5001)  # Change to any available port
```

### Missing API Keys
Make sure your `.env` file exists and contains valid API keys.

### Module Not Found
Run:
```bash
pip install -r requirements.txt
```

## Technologies Used

- **Backend**: Flask (Python web framework)
- **AI/ML**: LangChain, OpenAI GPT-4o, OpenAI Embeddings
- **Frontend**: HTML, CSS, JavaScript
- **Data**: JSON for structure, Text files for content
- **DevOps**: Docker, GitHub Actions CI/CD

## CI/CD & Deployment

This project uses GitHub Actions for automated CI/CD pipeline:

### Quick Deploy with Docker

```bash
# Pull the latest image
docker pull YOUR_USERNAME/drema-ai:latest

# Run with environment variables
docker run -d \
  -p 5000:5000 \
  -e OPENAI_API_KEY=your_openai_key \
  -e LANGCHAIN_PROJECT=DremaAI \
  --name drema-ai \
  YOUR_USERNAME/drema-ai:latest
```

Or use docker-compose:

```bash
# Create .env file with your API keys
cp .env.example .env
# Edit .env with your actual keys

# Start the application
docker-compose up -d
```

### CI/CD Pipeline

The pipeline automatically:
- ✅ Runs linting and tests on every PR
- 🐳 Builds Docker images
- 📦 Publishes to Docker Hub on main branch
- 🚀 Deploys to AWS automatically

For detailed CI/CD setup instructions, see [.github/workflows/README.md](.github/workflows/README.md)

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for various platforms.

## License

This project is for educational purposes.

## Support

For issues or questions, please check:
1. All dependencies are installed
2. API keys are correctly set in `.env`
3. Required data files (`category.json`, `topics.json`, `data/` folder) exist

For CI/CD issues, see [.github/workflows/README.md](.github/workflows/README.md)

