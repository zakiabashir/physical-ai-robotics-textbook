# Build Instructions

## Backend

The backend is a FastAPI application that requires Python 3.8+.

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=your_secret_key_here
BETTER_AUTH_SECRET=your_auth_secret_here

# AI Model
GEMINI_API_KEY=your_gemini_api_key

# RAG Configuration
COHERE_API_KEY=your_cohere_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

### Running the Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Frontend

The frontend is built with Docusaurus and requires Node.js 18.x (see `.nvmrc`).

### Important Note About Node.js Version

The project requires **Node.js 18.x**. Using Node.js 25+ will cause localStorage errors during build.

### Installation

```bash
cd frontend
npm install
```

### Local Development

```bash
npm start
```

### Build for Production

#### Standard Build (Requires Node.js 18.x)

```bash
npm run build
```

#### Build with localStorage Workaround (For Node.js 25+)

If you must use Node.js 25+, use the following command:

```bash
npm run build:vercel
```

This script:
1. Creates a localStorage.json file
2. Sets NODE_OPTIONS with localStorage file path
3. Runs the build process

### Windows Build Script

For Windows users, there's a batch file available:

```bash
build.bat
```

This handles the localStorage issue for Windows environments.

## Vercel Deployment

The project is configured for Vercel deployment with:

1. **vercel.json** - Main deployment configuration
2. **Node.js 18.x** specified in build config
3. **Custom build script** to handle localStorage issues

The build will automatically use Node.js 18.x on Vercel, which avoids the localStorage issue entirely.

## Environment Variables for Production

Make sure to set the following environment variables in your hosting platform:

- `DATABASE_URL`
- `SECRET_KEY`
- `BETTER_AUTH_SECRET`
- `GEMINI_API_KEY`
- `COHERE_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`

## Troubleshooting

### localStorage Error

If you encounter:
```
DOMException [SecurityError]: Cannot initialize local storage without a `--localstorage-file` path
```

Solution 1: Use Node.js 18.x (recommended)
```bash
nvm use 18
npm run build
```

Solution 2: Use the workaround script
```bash
npm run build:vercel
```

### Backend Import Errors

If you see import errors for RAG dependencies:

```bash
cd backend
pip install cohere qdrant-client trafilatura openai-agents
```

### Database Issues

For SQLite database issues:

```bash
cd backend
rm -f test.db  # Remove existing database
uvicorn app.main:app --reload  # Restart to recreate
```