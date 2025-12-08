# Railway Deployment Guide for Backend

## Overview
This guide will help you deploy the FastAPI backend to Railway and connect it with your Vercel frontend.

## Prerequisites
- Railway account (https://railway.app)
- GitHub account
- Required API keys:
  - Google Gemini API Key
  - Cohere API Key
  - Qdrant Vector Database URL and API Key

## Step 1: Prepare Your Repository

### 1.1 Ensure Railway Configuration is Ready
The `backend/railway.toml` is already configured correctly with:
- Builder: nixpacks
- Health check path: `/health`
- Restart policy on failure

### 1.2 Update Backend CORS Settings
First, let's update the backend to allow requests from your Vercel frontend:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

# Add this after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://physical-ai-robotics-textbook-8tzi59hee-zakiabashirs-projects.vercel.app",
        "http://localhost:3000",  # For local development
        "http://localhost:3001",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 2: Deploy to Railway

### 2.1 Connect Repository to Railway
1. Go to [Railway Dashboard](https://dashboard.railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your repository
5. Choose the `backend` directory as the root directory (if prompted)

### 2.2 Configure Environment Variables
In Railway dashboard, go to your project settings and add these environment variables:

#### Required Variables
```bash
# Application
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (Railway will provide this automatically when you add a PostgreSQL database)
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=models/gemini-2.0-flash

# Cohere AI
COHERE_API_KEY=your_cohere_api_key_here

# Qdrant Vector Database
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key

# Authentication
SECRET_KEY=generate_a_strong_random_secret_key_here
BETTER_AUTH_SECRET=another_strong_secret_for_auth
BETTER_AUTH_URL=https://your-frontend-domain.vercel.app

# Frontend URL (for CORS)
FRONTEND_URL=https://physical-ai-robotics-textbook-8tzi59hee-zakiabashirs-projects.vercel.app
```

### 2.3 Add Database Service
1. In your Railway project, click "New Service"
2. Select "Add Service" → "Database" → "PostgreSQL"
3. Railway will automatically provide the `DATABASE_URL`

### 2.4 Add Qdrant (Optional but Recommended)
1. Click "New Service" again
2. Select "Add Service" → "Docker"
3. Use the official Qdrant Docker image: `qdrant/qdrant:latest`
4. Expose port 6333
5. Add environment variables:
   - `QDRANT__SERVICE__HTTP_PORT=6333`

## Step 3: Update Frontend Configuration

### 3.1 Create Environment Configuration
Create a file `frontend/.env.production`:
```env
REACT_APP_API_URL=https://your-backend-production-url.railway.app
```

### 3.2 Update Frontend Components
Update API URLs in frontend components to use environment variables:

```javascript
// In components that make API calls, replace hardcoded URLs:
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

Key files to update:
- `frontend/src/components/ChatWidget/index.js`
- `frontend/src/components/ProgressTracker/index.js`
- `frontend/src/pages/RAGMonitor.js`
- `frontend/src/components/ChatAssistant/index.js`
- `frontend/src/components/ChatWidget/FeedbackComponent.jsx`

## Step 4: Deploy and Test

### 4.1 Deploy Backend
1. Push changes to GitHub
2. Railway will automatically deploy
3. Check the deployment logs for any errors
4. Test the health endpoint: `https://your-backend-url.railway.app/health`

### 4.2 Update Vercel Frontend
1. Add the backend URL as an environment variable in Vercel:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.railway.app`

2. Trigger a new deployment on Vercel

### 4.3 Test Connection
1. Visit your deployed frontend
2. Check browser network tab to ensure API calls go to the correct backend URL
3. Test key features:
   - Chat functionality
   - User authentication
   - Content loading
   - Progress tracking

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure the frontend URL is added to CORS origins in `main.py`
   - Check that `FRONTEND_URL` environment variable is set correctly

2. **Database Connection Errors**
   - Verify the `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/dbname`
   - Ensure PostgreSQL service is running in Railway

3. **API Key Errors**
   - Double-check all API keys are correctly set in Railway environment variables
   - Ensure no extra spaces or quotes in the values

4. **Build Failures**
   - Check Railway build logs
   - Ensure Python version is 3.11 or compatible
   - Verify all dependencies are in `requirements.txt`

## Railway-Specific Tips

### Automatic Deployments
- Railway automatically deploys on every push to the connected branch
- You can configure deployment triggers in Railway settings

### Scaling
- Railway supports auto-scaling based on traffic
- Monitor resource usage in Railway dashboard

### Logs
- Access real-time logs in Railway dashboard
- Use proper logging levels for debugging

### Custom Domain
- Add a custom domain in Railway settings if needed
- Update CORS origins to include the new domain

## Security Considerations

1. **API Keys**: Never commit API keys to Git. Always use environment variables.
2. **Database**: Ensure database is not publicly accessible.
3. **CORS**: Only allow specific origins, not wildcards.
4. **Rate Limiting**: The app already has rate limiting middleware.
5. **HTTPS**: Railway provides HTTPS automatically.

## Next Steps

1. Set up monitoring with Railway's built-in metrics
2. Configure error tracking (Sentry integration if needed)
3. Set up automated tests that run on deployment
4. Create a CI/CD pipeline for automated deployments

## Support

- Railway Documentation: https://docs.railway.app/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- For issues specific to this project, check the repository issues or create a new one.