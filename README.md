# Physical AI & Humanoid Robotics Textbook

An interactive technical textbook for learning Physical AI and Humanoid Robotics, combining theory, hands-on coding, and AI-powered assistance with advanced RAG technology.

[![Build Status](https://github.com/physical-ai/physical-ai-robotics-textbook/actions/workflows/deploy.yml/badge.svg)](https://github.com/physical-ai/physical-ai-robotics-textbook/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 🚀 Features

- **Interactive Content**: 12 comprehensive lessons across 4 chapters
- **RAG-Powered Chat Assistant**: Advanced AI assistant with Retrieval-Augmented Generation for accurate, textbook-based answers
- **Real-time Content Ingestion**: Automatically ingests and indexes textbook content for intelligent search
- **Interactive Code**: Run and modify Python, ROS 2, and Isaac code in your browser
- **Progress Tracking**: Monitor your learning journey with detailed statistics
- **Hands-on Labs**: Practical exercises and activities
- **Visual Learning**: Mermaid diagrams and visualizations
- **Assessments**: Interactive quizzes and knowledge checks
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## 📚 Curriculum

### Chapter 1: Physical AI Foundations
- Lesson 1: What is Physical AI?
- Lesson 2: Embodied Intelligence
- Lesson 3: Perception-Action Loops

### Chapter 2: Core Robotics Systems
- Lesson 1: ROS 2 Fundamentals
- Lesson 2: Gazebo Simulation
- Lesson 3: Unity Robotics Integration

### Chapter 3: AI-Robot Intelligence
- Lesson 1: NVIDIA Isaac Platform
- Lesson 2: Computer Vision for Robots
- Lesson 3: Vision-Language-Action (VLA) Systems

### Chapter 4: Humanoid Robotics Capstone
- Lesson 1: Humanoid Robot Kinematics
- Lesson 2: Biped Locomotion
- Lesson 3: Whole-Body Control
- Lesson 4: Autonomous Humanoid Project

## 🛠️ Tech Stack

### Frontend
- **Docusaurus 3.0**: Static site generator
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Monaco Editor**: Code editing
- **Framer Motion**: Animations
- **Axios**: HTTP client

### Backend
- **FastAPI**: Modern Python web framework
- **Google Gemini 2.0 Flash**: Advanced AI model for responses
- **Cohere**: High-quality text embeddings
- **Qdrant Cloud**: Vector database for semantic search and RAG
- **PostgreSQL**: Relational database
- **Redis**: Caching layer
- **SQLAlchemy**: ORM

### Infrastructure
- **Docker**: Containerization
- **GitHub Actions**: CI/CD
- **Nginx**: Reverse proxy
- **PostgreSQL**: Primary database

## 🤖 RAG Implementation

This textbook uses advanced Retrieval-Augmented Generation (RAG) to provide accurate, context-aware AI assistance:

### How RAG Works
1. **Content Ingestion**: Textbook content is automatically ingested from the sitemap
2. **Text Chunking**: Content is split into manageable chunks (1200 chars each)
3. **Embedding Generation**: Each chunk is converted to a 1024-dimensional vector using Cohere's embed-english-v3.0 model
4. **Vector Storage**: Embeddings are stored in Qdrant Cloud for fast similarity search
5. **Retrieval**: When you ask a question, relevant chunks are retrieved based on semantic similarity
6. **Generation**: Gemini 2.0 Flash uses only the retrieved content to generate accurate answers

### Key Features
- **Source Citation**: Every answer includes sources from the textbook
- **Relevance Scoring**: See how relevant each source is to your question
- **No Hallucination**: AI only uses information from the textbook
- **Context Awareness**: Understands which lesson/section you're viewing

### Ingestion API
The backend provides ingestion endpoints:
- `POST /api/v1/ingestion/all` - Ingest all content from sitemap
- `POST /api/v1/ingestion/url` - Ingest a single URL
- `GET /api/v1/ingestion/status` - Check ingestion status
- `POST /api/v1/ingestion/test` - Test ingestion with limited URLs

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+ and pip
- Docker and Docker Compose (optional)
- Google Gemini API key
- Cohere API key
- Qdrant Cloud account (or local Qdrant instance)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/physical-ai/physical-ai-robotics-textbook.git
cd physical-ai-robotics-textbook
```

2. **Set up environment variables**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend
cp .env.example .env.local
```

3. **Install dependencies**
```bash
# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

4. **Run the application**
```bash
# Development mode (both frontend and backend)
npm run dev

# Or run separately:
# Frontend
npm start

# Backend
cd backend && uvicorn app.main:app --reload
```

5. **Ingest Textbook Content** (Required for RAG functionality)
```bash
# Start the backend first
cd backend && uvicorn app.main:app --reload

# In another terminal, ingest all content
curl -X POST "http://localhost:8000/api/v1/ingestion/all" \
  -H "accept: application/json"

# Or test with limited URLs
curl -X POST "http://localhost:8000/api/v1/ingestion/test?limit=5" \
  -H "accept: application/json"
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Setup

Using Docker Compose is the easiest way to run the full stack:

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📖 Using the Textbook

### Navigation
- Use the sidebar to navigate between chapters and lessons
- The search bar helps find specific topics
- Progress is automatically saved as you complete lessons

### Interactive Features
- **Code Examples**: Click "Run Code" to execute Python examples
- **Edit Mode**: Modify code and see results instantly
- **AI Assistant**: Click "Ask Book" for help with any concept
- **Quizzes**: Test your understanding at the end of lessons
- **Activities**: Complete hands-on exercises to reinforce learning

### Getting Help
- Use the AI chat assistant for instant help
- Check the glossary for term definitions
- Review related concepts suggested by the AI
- Join our Discord community for peer support

## 🧪 Testing

### Frontend Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_chat.py
```

### Content Validation
```bash
# Validate all lesson files
npm run validate-content

# Validate specific file
node scripts/validate-content.js docs/chapter-1/lesson-1.mdx
```

## 📝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Content Contributions
1. Fork the repository
2. Create a feature branch
3. Add or modify lesson content in `/docs`
4. Run content validation
5. Submit a pull request

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- Qdrant for vector search capabilities
- Docusaurus team for the excellent documentation framework
- All contributors and early testers

## 📞 Support

- **Documentation**: [Full documentation](https://physical-ai-robotics.panaversity.org)
- **Discord**: [Join our community](https://discord.gg/physical-ai)
- **Issues**: [Report bugs](https://github.com/panaversity/physical-ai-robotics-textbook/issues)
- **Email**: support@panaversity.org

## 🗺️ Roadmap

- [ ] Multi-language support (Urdu, Spanish, Chinese)
- [ ] Advanced code execution environment
- [ ] Real-time collaborative features
- [ ] Mobile app
- [ ] Video content integration
- [ ] VR/AR visualization modes
- [ ] Instructor dashboard and analytics
- [ ] Certification program

---

Made with ❤️ by [Panaversity Institute](https://panaversity.org)