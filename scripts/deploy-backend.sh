#!/bin/bash

# Backend Deployment Script for Railway
# This script helps deploy the backend to Railway

echo "🚀 Deploying Physical AI Backend to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (uncomment if not logged in)
# railway login

# Navigate to backend directory
cd backend

# Initialize Railway project if not already done
if [ ! -f ".railway/config.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init
fi

# Add environment variables (replace with actual values)
echo "⚙️ Setting up environment variables..."

# You'll be prompted to enter these values
railway variables set DEBUG=false
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO

# Set your API keys
echo "🔑 Setting API keys..."
echo "Please enter your Gemini API Key:"
railway variables set GEMINI_API_KEY

echo "Please enter your Cohere API Key:"
railway variables set COHERE_API_KEY

echo "Please enter your Qdrant URL:"
railway variables set QDRANT_URL

echo "Please enter your Qdrant API Key:"
railway variables set QDRANT_API_KEY

echo "Please enter a secret key for JWT:"
railway variables set SECRET_KEY

echo "Please enter Better Auth secret:"
railway variables set BETTER_AUTH_SECRET

# Set frontend URL
railway variables set BETTER_AUTH_URL=https://physical-ai-robotics-textbook-8tzi59hee-zakiabashirs-projects.vercel.app

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment started! Check your Railway dashboard for status."