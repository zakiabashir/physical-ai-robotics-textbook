# Quick Deployment Steps

## Backend Deployment on Railway

### 1. Prepare API Keys
Before starting, make sure you have:
- Google Gemini API Key
- Cohere API Key
- Qdrant Cluster URL and API Key

### 2. Deploy to Railway

#### Option A: Using Railway Dashboard
1. Go to [Railway Dashboard](https://dashboard.railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set root directory to `backend`
5. Add a PostgreSQL database service
6. Add environment variables:

```bash
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
GEMINI_API_KEY=your_gemini_key_here
COHERE_API_KEY=your_cohere_key_here
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
SECRET_KEY=generate_strong_secret_here
BETTER_AUTH_SECRET=another_strong_secret
BETTER_AUTH_URL=https://physical-ai-robotics-textbook-8tzi59hee-zakiabashirs-projects.vercel.app
```

7. Deploy

#### Option B: Using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to project
cd backend

# Deploy
railway up

# Set environment variables in Railway dashboard
```

### 3. After Deployment
1. Note your Railway backend URL (e.g., `https://your-app.railway.app`)
2. Test health endpoint: `https://your-app.railway.app/health`
3. Test API docs: `https://your-app.railway.app/docs`

## Frontend Configuration

### 1. Update Vercel Environment Variable
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add: `REACT_APP_API_URL` = `https://your-backend-url.railway.app`

### 2. Redeploy Frontend
Push any change or trigger redeploy in Vercel dashboard

## Important Notes

1. **Database**: Railway provides the `DATABASE_URL` automatically when you add PostgreSQL
2. **CORS**: Already configured for your Vercel URL in backend
3. **Local Development**: Frontend will still use localhost:8000 for local development
4. **API Keys**: Never commit API keys to Git. Always use environment variables

## Testing Connection

After both are deployed:

1. Visit your frontend on Vercel
2. Open browser DevTools → Network tab
3. Look for API calls - they should go to your Railway URL
4. Test chat functionality to ensure backend connection works

## Getting Help

- Railway Documentation: https://docs.railway.app/
- Vercel Documentation: https://vercel.com/docs
- Check deployment logs in both dashboards for errors