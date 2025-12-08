# 🚀 Deployment Guide

This guide explains how to deploy the Physical AI & Humanoid Robotics Textbook to production.

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Google Gemini API key
- Domain name (optional)

## 🏃 Deployment Options

### Option 1: Development/Staging (Local)

#### Backend
```bash
cd backend
copy .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
npm install
npm start
```

### Option 2: Production with Docker Compose

1. **Create production environment file**:
```bash
cp .env.example .env
# Edit with production values
```

2. **Start all services**:
```bash
docker-compose -f docker-compose.yml up -d
```

3. **Access the application**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 3: Production in the Cloud

#### A. Deploy Frontend to GitHub Pages

1. Push to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. GitHub Actions will automatically build and deploy to GitHub Pages

#### B. Deploy Backend to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway link
railway up
```

#### C. Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy backend:
```bash
cd backend
vercel --prod
```

### Option 4: Full Production Setup

1. **Prepare SSL certificates**:
```bash
# Create SSL directory
mkdir ssl

# Add your certificates
# - cert.pem (certificate)
# - key.pem (private key)
```

2. **Start with Docker Compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

Backend (`.env`):
```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=models/gemini-2.5-flash

# Security
SECRET_KEY=your_super_secret_key
BETTER_AUTH_SECRET=your_auth_secret

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_key
```

### Domain Configuration

1. **Update domain in**:
   - `docusaurus.config.js`
   - `nginx.conf`
   - Docker Compose files

2. **Configure DNS**:
   - A record: `@` → your-server-ip
   - CNAME: `www` → `your-domain.com`

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit API keys to Git
- Use `.env.example` as template
- Use different keys for dev/staging/prod

### 2. SSL/TLS
- Always use HTTPS in production
- Use strong SSL certificates
- Configure HSTS headers

### 3. Rate Limiting
- Implemented in Nginx configuration
- API: 10 requests/second
- Static: 30 requests/second

### 4. Database Security
- Use connection pooling
- Enable SSL for database connections
- Regular backups

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: Automatic health page
- Load balancer health checks

### Logging
- Backend: Application logs
- Nginx: Access and error logs
- Railway: Application metrics

### Metrics
- Response time monitoring
- Error rate tracking
- User analytics

## 🚀 CI/CD Pipeline

### GitHub Actions
- **`.github/workflows/deploy-frontend.yml`**: Frontend auto-deploy
- Automated testing on push
- Build validation

### Testing Pipeline
1. Unit tests
2. Integration tests
3. E2E tests
4. Performance tests

## 📋 Deployment Checklist

- [ ] API keys configured
- [ ] Environment variables set
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Health checks passing
- [ ] Logs configured
- [ ] Monitoring set up
- [ ] Backup strategy in place

## 🔧 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Linux/macOS
sudo lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
tasklist | findstr node
taskkill /F /PID [PID]
```

**2. Database Connection Issues**
- Check connection string
- Verify database is running
- Check firewall rules

**3. CORS Errors**
- Verify CORS origins in backend
- Check API URL configuration
- Ensure both services are running

**4. Build Failures**
- Check Node.js version
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall

## 🎯 Production Best Practices

1. **Use Environment Variables**
   - No hardcoded secrets
   - Different configs per environment

2. **Implement Caching**
   - Static assets
   - API responses
   - Database queries

3. **Monitor Performance**
   - Page load time
   - API response time
   - Error rates

4. **Regular Updates**
   - Security patches
   - Dependency updates
   - SSL certificate renewals

## 📚 Next Steps

After deployment:

1. **Verify all features work**
   - Chat assistant
   - Interactive code
   - Progress tracking

2. **Monitor performance**
   - Set up alerts
   - Review logs regularly

3. **Collect feedback**
   - User testing
   - Bug reports
   - Feature requests

## 🆘 Support

For deployment issues:
- Check logs in the console
- Review configuration files
- Test locally first

For application issues:
- Review error messages
- Check browser console
- Verify API connectivity

## 📞 Contact

- Repository: https://github.com/panaversity/physical-ai-robotics-textbook
- Documentation: See STARTUP_GUIDE.md
- Issues: Create an issue on GitHub