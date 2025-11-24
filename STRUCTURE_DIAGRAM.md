# Project Structure Visualization

## Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                         app.py                              │
│                  (Application Factory)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─────────────────────────────────────┐
                     │                                     │
                     ▼                                     ▼
        ┌────────────────────────┐          ┌────────────────────────┐
        │    src/config.py       │          │    src/routes.py       │
        │  (Configuration)       │          │   (Route Handlers)     │
        │                        │          │                        │
        │  - Load env vars       │          │  - GET /               │
        │  - Initialize LLM      │          │  - GET /get_classes    │
        │  - Initialize embeddings│         │  - GET /get_subjects   │
        └────────────┬───────────┘          │  - GET /get_topics     │
                     │                      │  - POST /generate      │
                     │                      └───────┬────────────────┘
                     │                              │
                     │                              │
                     ▼                              ▼
        ┌────────────────────────────────────────────────────────┐
        │              src/components/                           │
        ├────────────────────────────────────────────────────────┤
        │                                                        │
        │  ┌──────────────────────────┐  ┌──────────────────┐  │
        │  │ content_fetcher.py       │  │ mcq_generator.py │  │
        │  │                          │  │                  │  │
        │  │ - get_boards()           │  │ - generate_mcqs()│  │
        │  │ - get_classes()          │  │ - create_prompt()│  │
        │  │ - get_subjects()         │  │ - parse_response()│ │
        │  │ - get_topics()           │  │                  │  │
        │  │ - fetch_content()        │  │                  │  │
        │  └──────────────────────────┘  └──────────────────┘  │
        │                                                        │
        └────────────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │      src/utils/            │
        ├────────────────────────────┤
        │                            │
        │  common.py                 │
        │  - validate_difficulty()   │
        │  - validate_num_questions()│
        │  - format_topic_name()     │
        │  - clean_json_response()   │
        │                            │
        └────────────────────────────┘
```

## Data Flow

```
User Request
     │
     ▼
┌─────────────────┐
│  Browser/UI     │
│  (index.html)   │
└────────┬────────┘
         │
         │ HTTP Request
         ▼
┌─────────────────┐
│  Flask Routes   │
│  (routes.py)    │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│ Content Fetcher  │  │  MCQ Generator   │
│                  │  │                  │
│ 1. Load JSON     │  │ 1. Create prompt │
│ 2. Find book     │  │ 2. Call LLM      │
│ 3. Extract topic │  │ 3. Parse JSON    │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│  Data Files      │  │   Groq LLM       │
│  (data/*.txt)    │  │  (Cloud API)     │
└──────────────────┘  └──────────────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────┐
         │  JSON Response  │
         │  (MCQs)         │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Browser/UI     │
         │  (Display)      │
         └─────────────────┘
```

## File Organization

```
src/
│
├── __init__.py                 # Package initialization
│   └── Exports: Config, Routes
│
├── config.py                   # Configuration management
│   ├── Class: Config
│   ├── Methods:
│   │   ├── __init__()
│   │   ├── initialize_llm()
│   │   ├── initialize_embeddings()
│   │   ├── get_llm()
│   │   └── get_embeddings()
│   └── Dependencies: dotenv, langchain_groq, langchain_huggingface
│
├── routes.py                   # Flask route handlers
│   ├── Class: Routes
│   ├── Methods:
│   │   ├── __init__(app, fetcher, mcq_generator)
│   │   ├── register_routes()
│   │   ├── index()
│   │   ├── get_classes(board)
│   │   ├── get_subjects(board, class_num)
│   │   ├── get_topics(board, class_num, subject)
│   │   └── generate()
│   └── Dependencies: flask, components
│
├── components/
│   ├── __init__.py             # Component exports
│   │   └── Exports: EducationContentFetcher, MCQGenerator
│   │
│   ├── content_fetcher.py      # Content fetching logic
│   │   ├── Class: EducationContentFetcher
│   │   ├── Methods:
│   │   │   ├── __init__(category_file, topics_file, data_folder)
│   │   │   ├── get_boards()
│   │   │   ├── get_classes(board)
│   │   │   ├── get_subjects(board, class_num)
│   │   │   ├── get_topics(board, class_num, subject)
│   │   │   ├── get_books(board, class_num, subject)
│   │   │   ├── extract_topic_from_book(book_content, topic_num)
│   │   │   └── fetch_content(board, class_num, subject, topic_num)
│   │   └── Dependencies: os, json, re
│   │
│   ├── mcq_generator.py        # MCQ generation logic
│   │   ├── Class: MCQGenerator
│   │   ├── Methods:
│   │   │   ├── __init__(llm)
│   │   │   └── generate_mcqs(num_questions, difficulty_level, topic, content)
│   │   └── Dependencies: langchain.prompts, json
│   │
│   └── loader.py               # (Reserved for future use)
│
└── utils/
    ├── __init__.py             # Utility exports
    │   └── Exports: validate_difficulty_level, validate_num_questions,
    │                format_topic_name, clean_json_response
    │
    ├── common.py               # Common utilities
    │   ├── Functions:
    │   │   ├── validate_difficulty_level(difficulty)
    │   │   ├── validate_num_questions(num)
    │   │   ├── format_topic_name(topic_num, topic_name)
    │   │   └── clean_json_response(response_text)
    │   └── Dependencies: None (pure Python)
    │
    └── caching.py              # (Reserved for caching)
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interaction Flow                        │
└─────────────────────────────────────────────────────────────────┘

1. User Opens Browser
   └─> GET / → routes.index() → render_template('index.html')

2. User Selects Board
   └─> GET /get_classes/CBSE → routes.get_classes('CBSE')
       └─> fetcher.get_classes('CBSE') → Return JSON

3. User Selects Class
   └─> GET /get_subjects/CBSE/11 → routes.get_subjects('CBSE', '11')
       └─> fetcher.get_subjects('CBSE', '11') → Return JSON

4. User Selects Subject
   └─> GET /get_topics/CBSE/11/Physics → routes.get_topics(...)
       └─> fetcher.get_topics(...) → Return JSON

5. User Submits Form
   └─> POST /generate → routes.generate()
       ├─> fetcher.fetch_content(...) → Get topic content
       └─> mcq_generator.generate_mcqs(...) → Generate MCQs
           └─> LLM API Call → Parse Response → Return MCQs
```

## Class Relationships

```
┌──────────────┐
│    Config    │
│              │
│ + llm        │◄─────────────────┐
│ + embeddings │                  │
└──────────────┘                  │
                                  │
                                  │ Uses
┌──────────────┐                  │
│ MCQGenerator │                  │
│              │                  │
│ - llm        │──────────────────┘
│              │
│ + generate() │
└──────────────┘


┌──────────────────────┐
│ EducationContent     │
│ Fetcher              │
│                      │
│ - category_data      │
│ - topics_data        │
│ - data_folder        │
│                      │
│ + get_boards()       │
│ + get_classes()      │
│ + get_subjects()     │
│ + get_topics()       │
│ + fetch_content()    │
└──────────────────────┘


┌──────────────────────┐
│      Routes          │
│                      │
│ - app                │
│ - fetcher            │──────► Uses EducationContentFetcher
│ - mcq_generator      │──────► Uses MCQGenerator
│                      │
│ + register_routes()  │
│ + index()            │
│ + get_classes()      │
│ + get_subjects()     │
│ + get_topics()       │
│ + generate()         │
└──────────────────────┘
```

This visualization shows how all components work together in the modularized structure!
