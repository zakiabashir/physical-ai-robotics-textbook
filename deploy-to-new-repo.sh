#!/bin/bash

# Deploy Physical AI Textbook to a new GitHub repository
# Usage: ./deploy-to-new-repo.sh [new-repo-name]

REPO_NAME=${1:-"physical-ai-robotics-textbook"}
GITHUB_USERNAME=${2:-$(git config user.name)}

echo "🚀 Deploying Physical AI Textbook to new repository..."
echo "Repository: $REPO_NAME"
echo "Username: $GITHUB_USERNAME"
echo ""

# Create a new directory for the clean repository
echo "📁 Creating clean repository directory..."
mkdir -p ../$REPO_NAME
cd ../$REPO_NAME

# Initialize new git repository
echo "🔧 Initializing git repository..."
git init

# Configure git
git config user.name "$GITHUB_USERNAME"
git config user.email "$(git config user.email)"

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << EOL
# Dependencies
node_modules/
venv/
env/
.env

# Build outputs
build/
dist/
__pycache__/
*.pyc
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# API Keys
.env
.env.local
.env.production
EOL

# Copy all files from the original repository
echo "📋 Copying files..."
cp -r ../physical_AI_book_hacka/* .
rm -rf .git
cp -r ../physical_AI_book_hacka/.git .
git remote -v

# Remove the old remote and add new one
echo "🔗 Setting up new remote..."
git remote remove origin
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Create initial commit
echo "💾 Creating initial commit..."
git add .
git commit -m "Initial commit: Physical AI & Humanoid Robotics Interactive Textbook

✨ Features:
- FastAPI backend with RAG system
- Docusaurus frontend documentation
- AI-powered chat assistant with Google Gemini
- Code execution with StackBlitz WebContainers
- Personalized learning and progress tracking
- ROS 2 integration support

🔧 Tech Stack:
- Backend: Python, FastAPI, SQLAlchemy
- Frontend: React, Docusaurus
- Database: SQLite (dev), PostgreSQL (prod)
- Vector DB: Qdrant Cloud
- AI: Google Gemini 2.0 Flash

📚 Deployment ready for GitHub Pages and Railway/Render"

# Instructions for creating repository on GitHub
echo ""
echo "🎯 Next Steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: Physical AI & Humanoid Robotics Interactive Textbook"
echo "   - Public repository"
echo "   - Don't initialize with README (we have one)"
echo ""
echo "2. After creating the repository, push the code:"
echo "   git push -u origin main"
echo ""
echo "3. Configure GitHub Pages:"
echo "   - Go to Settings > Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main"
echo "   - Folder: /root"
echo ""
echo "4. Set up environment variables in your repository:"
echo "   - GEMINI_API_KEY"
echo "   - QDRANT_API_KEY"
echo "   - QDRANT_URL"
echo "   - SECRET_KEY"
echo ""
echo "✅ Your code is ready in: $(pwd)"
echo "🌐 Repository will be: https://github.com/$GITHUB_USERNAME/$REPO_NAME"