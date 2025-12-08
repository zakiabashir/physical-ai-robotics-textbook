# 🚀 Physical AI Textbook - Startup Guide

## Quick Start

### 1. Backend Setup (Optional - for AI Assistant)
```bash
cd backend
```
Create `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start backend:
```bash
uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`

### 2. Frontend Setup
**Option A: Using the batch file (Windows)**
```bash
start-frontend.bat
```

**Option B: Manual setup**
```bash
# Install dependencies
npm install

# Start the development server
npm start
```

Frontend will run on: `http://localhost:3000`

### 3. What's Available

#### Frontend (http://localhost:3000)
- **Interactive Textbook**: 4 chapters, 13 lessons
- **AI Chat Assistant**: Click "Ask Book" button
- **Interactive Code**: Edit and run code examples
- **Quizzes**: Test your knowledge
- **Progress Tracking**: Monitor your learning journey

#### Backend API (http://localhost:8000)
- **Chat API**: `/api/v1/chat/`
- **Content API**: `/api/v1/content/`
- **Embeddings**: `/api/v1/embeddings/`
- **Authentication**: `/api/v1/auth/`

## 📋 Available Lessons

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
- Lesson 3: Vision-Language-Action Systems

### Chapter 4: Humanoid Robotics Capstone
- Lesson 1: Humanoid Kinematics
- Lesson 2: Biped Locomotion
- Lesson 3: Whole-Body Control
- Lesson 4: Autonomous Humanoid Project

## 🔧 Troubleshooting

### Frontend Issues
1. **Port already in use**:
   ```bash
   PORT=3001 npm start
   ```

2. **Dependencies missing**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

3. **Build errors**:
   - Check Node.js version: `node --version` (should be 18+)
   - Clear cache: `npm run clear`

### Backend Issues
1. **Gemini API errors**:
   - Verify your API key in `.env`
   - Check quota limits at: https://aistudio.google.com

2. **Database errors**:
   - Database is optional for basic use
   - For full features, configure PostgreSQL in `.env`

## 🌟 Features

- ✅ **AI-Powered Chat**: Google Gemini integration
- ✅ **Interactive Code**: Monaco Editor with syntax highlighting
- ✅ **Progress Tracking**: Visual progress indicators
- ✅ **Responsive Design**: Works on mobile and desktop
- ✅ **Dark/Light Theme**: Toggle between themes
- ✅ **Mermaid Diagrams**: Visual concept explanations
- ✅ **Assessments**: Interactive quizzes

## 📚 Next Steps

1. **Start Learning**: Navigate through chapters
2. **Try AI Assistant**: Ask questions about the content
3. **Run Code Examples**: Test robotics code in browser
4. **Complete Quizzes**: Check your understanding
5. **Build Capstone**: Complete the humanoid robot project

## 🛠 Development

For developers wanting to extend the project:

### Adding New Lessons
1. Create `.mdx` file in `docs/chapter-X/`
2. Add to `sidebars.js`
3. Use MDX components for interactivity

### Frontend Components
- Location: `src/components/`
- ChatWidget: AI assistant interface
- InteractiveCode: Code editor with execution
- Quiz: Interactive assessments

### Backend Services
- Location: `backend/app/services/`
- Gemini Client: AI integration
- Qdrant Client: Vector search
- Content Parser: MDX processing

Happy Learning! 🎓