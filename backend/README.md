# Physical AI & Humanoid Robotics Textbook - Backend API

FastAPI backend for the interactive Physical AI textbook.

## Features

- **AI-powered Chat Assistant**: Context-aware chatbot powered by OpenAI
- **Vector Search**: Semantic content search using Qdrant
- **User Authentication**: JWT-based authentication system
- **Content Management**: MDX content parsing and serving
- **Progress Tracking**: User learning progress management

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:
   - OpenAI API key
   - Qdrant connection details
   - Database connection string
   - Secret keys

4. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Register a new user
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /me` - Get current user info
- `GET /conversations` - Get user conversation history

### Chat (`/api/v1/chat`)
- `POST /` - Send a chat message
- `GET /conversations/{id}` - Get conversation history
- `POST /feedback` - Submit feedback

### Embeddings (`/api/v1/embeddings`)
- `POST /index/content` - Index textbook content
- `GET /search` - Search content
- `GET /suggest` - Get lesson suggestions
- `POST /upload` - Upload and index a file

### Content (`/api/v1/content`)
- `GET /chapters` - Get all chapters
- `GET /chapters/{id}` - Get specific chapter
- `GET /lessons/{chapter}/{lesson}` - Get lesson content
- `GET /navigation` - Get navigation structure

## Architecture

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Qdrant**: Vector database for semantic search
- **OpenAI**: AI model for chat responses
- **JWT**: Token-based authentication

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
isort app/
```

Lint:
```bash
flake8 app/
```