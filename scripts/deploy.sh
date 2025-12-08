#!/bin/bash

# Physical AI & Humanoid Robotics Textbook - Production Deployment Script
# This script deploys the full stack to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print() {
    echo -e "${NC}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python is not installed"
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Docker deployment requires Docker."
    fi

    # Check git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Deploy frontend to GitHub Pages
deploy_frontend() {
    print_info "Deploying frontend to GitHub Pages..."

    # Build frontend
    print_info "Building frontend..."
    npm run build

    # Deploy to GitHub Pages
    if command -v gh &> /dev/null; then
        gh-pages -d build
        print_success "Frontend deployed to GitHub Pages"
    else
        print_warning "gh-pages CLI not found. Manual deployment required."
        print_info "To deploy manually:"
        print "  1. Run: npm run build"
        print "  2. Push the 'build' folder to your gh-pages branch"
    fi
}

# Deploy backend to Railway
deploy_backend_railway() {
    print_info "Deploying backend to Railway..."

    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Install it with: npm install -g @railway/cli"
        exit 1
    fi

    # Login to Railway (if not logged in)
    if ! railway whoami &> /dev/null; then
        print_info "Please login to Railway..."
        railway login
    fi

    # Deploy
    cd backend
    railway up
    cd ..

    print_success "Backend deployed to Railway"
}

# Deploy backend to Vercel
deploy_backend_vercel() {
    print_info "Deploying backend to Vercel..."

    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI is not installed. Install it with: npm i -g vercel"
        exit 1
    fi

    cd backend
    vercel --prod
    cd ..

    print_success "Backend deployed to Vercel"
}

# Full Docker deployment
deploy_docker() {
    print_info "Deploying with Docker Compose..."

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    # Build and start services
    if docker compose version &> /dev/null; then
        docker compose -f docker-compose.prod.yml up -d --build
    else
        docker-compose -f docker-compose.prod.yml up -d --build
    fi

    print_success "Docker deployment complete"
}

# Production environment setup
setup_production_env() {
    print_info "Setting up production environment..."

    # Create production .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating template..."
        cat > .env << EOF
# Production Environment Variables
# GEMINI_API_KEY=your_production_gemini_api_key
# SECRET_KEY=your_production_secret_key
# BETTER_AUTH_SECRET=your_production_auth_secret
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
# QDRANT_URL=https://your-qdrant-instance.com
# QDRANT_API_KEY=your_qdrant_api_key

# Optional: Analytics
# GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
EOF
        print_warning "Please fill in the .env file with your production values"
    fi

    # Verify SSL certificates (if using nginx)
    if [ -d "ssl" ]; then
        if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
            print_warning "SSL certificates not found in ssl/ directory"
            print_info "To enable HTTPS, add your certificates to ssl/"
        fi
    fi
}

# Run tests before deployment
run_tests() {
    print_info "Running pre-deployment tests..."

    # Frontend tests
    if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
        print_info "Running frontend tests..."
        npm test
    fi

    # Backend tests
    if [ -f "backend/requirements.txt" ] && [ -f "backend/test_server.py" ]; then
        print_info "Running backend tests..."
        cd backend
        python test_server.py &
        SERVER_PID=$!
        sleep 3

        # Test health endpoint
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend health check passed"
        else
            print_error "Backend health check failed"
            kill $SERVER_PID 2>/dev/null || true
            exit 1
        fi

        kill $SERVER_PID 2>/dev/null || true
        cd ..
    fi

    print_success "All tests passed"
}

# Health check after deployment
health_check() {
    print_info "Performing health checks..."

    # Check frontend
    if curl -f https://physical-ai-robotics.panaversity.org > /dev/null 2>&1; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend health check failed"
    fi

    # Check backend (update URL to your actual backend URL)
    BACKEND_URL="https://api.physical-ai-robotics.panaversity.org"
    if curl -f $BACKEND_URL/health > /dev/null 2>&1; then
        print_success "Backend is accessible"
    else
        print_warning "Backend health check failed"
    fi
}

# Main deployment function
main() {
    print "======================================="
    print "Physical AI Textbook Deployment"
    print "======================================="

    # Check deployment mode
    if [ "$1" = "frontend" ]; then
        check_prerequisites
        run_tests
        setup_production_env
        deploy_frontend
        health_check
    elif [ "$1" = "backend-railway" ]; then
        check_prerequisites
        run_tests
        setup_production_env
        deploy_backend_railway
        health_check
    elif [ "$1" = "backend-vercel" ]; then
        check_prerequisites
        run_tests
        setup_production_env
        deploy_backend_vercel
        health_check
    elif [ "$1" = "docker" ]; then
        check_prerequisites
        run_tests
        setup_production_env
        deploy_docker
        health_check
    elif [ "$1" = "all" ]; then
        check_prerequisites
        run_tests
        setup_production_env
        deploy_frontend
        deploy_backend_railway
        health_check
    else
        print_info "Usage: $0 [frontend|backend-railway|backend-vercel|docker|all]"
        print ""
        print "  frontend        - Deploy frontend to GitHub Pages"
        print "  backend-railway  - Deploy backend to Railway"
        print "  backend-vercel   - Deploy backend to Vercel"
        print "  docker          - Deploy full stack with Docker"
        print "  all             - Deploy frontend and backend (Railway)"
        exit 1
    fi

    print ""
    print_success "Deployment completed successfully!"
    print ""
    print_info "Next steps:"
    print "  1. Update your DNS settings if needed"
    print "  2. Monitor your deployment"
    print "  3. Set up alerts and monitoring"
    print ""
}

# Run main function with all arguments
main "$@"