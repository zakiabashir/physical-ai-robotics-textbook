# Physical AI & Humanoid Robotics Textbook - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Physical AI & Humanoid Robotics Textbook application to production.

## Prerequisites

### Required Services
- **Google Gemini API Key**: For AI chat functionality
- **Qdrant Cloud Account**: For vector database
- **GitHub Repository**: For code hosting and CI/CD

### Software Requirements
- Node.js 18.x (NOT 25+ due to localStorage compatibility issues)
- Python 3.8+
- Git

## Local Development Setup

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/physical-ai/physical-ai-robotics-textbook.git
   cd physical-ai-robotics-textbook/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. **Initialize database**:
   ```bash
   python -m app.database.init_db
   ```

6. **Run the backend server**:
   ```bash
   # Default port 8000 (use alternative if blocked)
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Build the frontend**:
   ```bash
   # Use the build script to handle localStorage issues
   ./build-vercel.sh
   ```

4. **Run development server**:
   ```bash
   npm start
   # Or serve built files
   npx docusaurus serve --port 3001
   ```

## Production Deployment

### GitHub Pages Deployment

The application is configured to deploy to GitHub Pages using GitHub Actions.

1. **Enable GitHub Pages**:
   - Go to repository Settings > Pages
   - Select "GitHub Actions" as the source

2. **Configure Environment Secrets**:
   - `GEMINI_API_KEY`: Google Gemini API key
   - `QDRANT_API_KEY`: Qdrant Cloud API key
   - `QDRANT_URL`: Qdrant Cloud URL
   - `SECRET_KEY`: JWT secret key for authentication

3. **Push to deploy**:
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

4. **Monitor deployment**:
   - Go to Actions tab to see build status
   - Once complete, site will be available at `https://physical-ai-robotics.org`

### Backend Deployment Options

#### Option 1: Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Configure environment variables in Railway dashboard
3. Deploy automatically on push to main branch

#### Option 2: Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Configure environment variables

#### Option 3: Vercel Serverless
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel --prod` in backend directory
3. Configure serverless function to handle API routes

### Environment Variables

Backend (.env):
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./physical_ai.db

# AI Services
GEMINI_API_KEY=your_gemini_api_key
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_cloud_url

# Authentication
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["https://physical-ai-robotics.org"]

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

Frontend (docusaurus.config.js):
```javascript
const config = {
  url: 'https://physical-ai-robotics.org',
  baseUrl: '/',
  trailingSlash: false,
  organizationName: 'physical-ai',
  projectName: 'physical-ai-robotics-textbook'
}
```

## API Integration

### Frontend API Configuration

The frontend automatically detects the backend URL:
- Development: Uses `http://localhost:8001`
- Production: Uses `https://physical-ai-backend.onrender.com` (or your backend URL)

To update the backend URL:
```javascript
// frontend/src/config.js
export const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://your-backend-url.com'
  : 'http://localhost:8001';
```

## Monitoring and Maintenance

### Health Checks

- **Backend Health**: `GET /health`
- **API Info**: `GET /api/v1/info`
- **Database Status**: Check health endpoint for database connection

### Logs

- **Backend**: Logs are written to console and can be configured to write to files
- **Frontend**: Build logs in GitHub Actions, runtime logs in browser console

### Performance Monitoring

Consider integrating:
- **Frontend**: Google Analytics, Vercel Analytics
- **Backend**: Sentry for error tracking, custom metrics for API performance

## Troubleshooting

### Common Issues

1. **localStorage error during build**:
   - Use Node.js 18.x, not 25+
   - Run `./build-vercel.sh` instead of `npm run build`

2. **Port 8000 blocked**:
   - Use alternative port (e.g., 8001): `--port 8001`

3. **CORS errors**:
   - Update CORS_ORIGINS in backend .env
   - Ensure frontend URL is whitelisted

4. **API key errors**:
   - Verify all environment variables are set
   - Check API key permissions and quotas

5. **Build failures**:
   - Check Node.js version (must be 18.x)
   - Clear npm cache: `npm cache clean --force`

### Getting Help

1. Check logs in GitHub Actions
2. Review error messages in browser console
3. Verify environment variables
4. Check API service status (Gemini, Qdrant)

## Security Considerations

1. **API Keys**: Never commit API keys to repository
2. **HTTPS**: Always use HTTPS in production
3. **Environment Variables**: Use different keys for development and production
4. **Rate Limiting**: Configure rate limiting for API endpoints
5. **Authentication**: Secure JWT tokens with proper expiration

## Continuous Deployment

The GitHub Actions workflow automatically:
1. Runs tests on every push
2. Builds frontend on push to main
3. Deploys to GitHub Pages
4. Notifies of deployment status

To modify deployment:
- Edit `.github/workflows/deploy-pages.yml`
- Adjust build steps or add environment checks

## Scaling Considerations

- **Database**: Consider PostgreSQL for production instead of SQLite
- **Caching**: Add Redis for caching responses
- **CDN**: Use CDN for static assets
- **Load Balancer**: For high-traffic scenarios
- **Monitoring**: Implement comprehensive monitoring

## Summary

The Physical AI & Humanoid Robotics Textbook is now fully configured for production deployment with:
- ✅ Frontend deployed to GitHub Pages
- ✅ Backend API with all endpoints functional
- ✅ Authentication and personalization features
- ✅ Code execution simulation
- ✅ AI-powered chat assistant
- ✅ Interactive lessons and progress tracking

For any deployment issues, refer to the troubleshooting section or check the GitHub Actions logs.