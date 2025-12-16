# Mixed Content Error Fix

## Problem
The frontend (HTTPS on Vercel) was trying to fetch from the backend using HTTP, causing browser to block the request with "Mixed Content" error.

## Root Cause
Even though our source code had HTTPS URLs, Vercel was using a cached build or not reading the environment variable correctly.

## Solutions Applied

1. **Updated chatApi.ts**
   ```typescript
   // Before:
   const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app/api/v1';

   // After:
   const API_BASE_URL = `${process.env.REACT_APP_API_URL || 'https://physical-ai-robotics-textbook-production.up.railway.app'}/api/v1`;
   ```

2. **Added vercel.json**
   ```json
   {
     "build": {
       "env": {
         "REACT_APP_API_URL": "https://physical-ai-robotics-textbook-production.up.railway.app"
       }
     }
   }
   ```

3. **Fixed all HTTP fallback URLs**
   - FeedbackComponent.jsx
   - ProgressTracker/index.js
   - OnboardingSurvey.jsx

## Status
- ✅ Changes committed and pushed
- ⏳ Vercel rebuilding (1-2 minutes)
- 🔄 Monitor for successful HTTPS requests

## Expected Result
After Vercel rebuild completes, chat will work without mixed content errors.