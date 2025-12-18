# Authentication Fixes and Google Sign-In Setup

## Issues Fixed

### 1. "process is not defined" Error
**Problem**: The authentication context was using `process.env` which is not available in the browser environment.

**Solution**: Replaced `process.env.API_BASE_URL` with hardcoded API URL in AuthContext.

### 2. Google Sign-In Implementation
Added Google Sign-In UI components to both login and signup forms with a divider showing "OR" between regular and Google authentication options.

## Current Status

### ✅ Working
- Email/password authentication
- JWT token management
- Persistent login state
- Protected chat access
- Modern UI with gradients

### ⚠️ Google Sign-In (UI Ready, Needs Configuration)
The Google Sign-In button is visible but shows a message: "Google Sign-In requires Google OAuth configuration. Please use email/password for now."

## To Enable Google Sign-In

### Prerequisites
1. Google Cloud Console account
2. Domain ownership (for production)

### Steps to Configure

1. **Create Google OAuth 2.0 Client ID**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project or create a new one
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Select "Web application"
   - Add authorized origins:
     - `https://physical-ai-robotics.org` (production)
     - `http://localhost:3000` (development)
   - Add authorized redirect URIs:
     - `https://physical-ai-robotics.org`
     - `http://localhost:3000`

2. **Get Client ID and Secret**
   - Note down the Client ID and Client Secret
   - Keep the Client Secret secure (backend only)

3. **Configure Frontend**
   Update `frontend/src/components/Auth/GoogleSignIn.js`:
   ```javascript
   window.google.accounts.id.initialize({
     client_id: 'YOUR_GOOGLE_CLIENT_ID_HERE',
     // ... rest of configuration
   });
   ```

4. **Configure Backend**
   Add to `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   ```

5. **Deploy Backend**
   - Push changes with new environment variables
   - Railway will pick up the new environment variables

### Alternative: Simplified Google Sign-In
For immediate implementation without full OAuth setup, you can use Google's basic sign-in button with their JavaScript client library.

## Authentication Flow

1. **Unauthenticated User**
   - Clicks chat button
   - Sees login modal with options:
     - Email/password form
     - Google Sign-In button

2. **Email/Password Login**
   - Enter credentials
   - Receive JWT token
   - Store in localStorage
   - Chat opens

3. **Google Sign-In** (When configured)
   - Click Google button
   - Google OAuth popup
   - Receive Google ID token
   - Send to backend for verification
   - Receive JWT token
   - Store and open chat

## Security Considerations

- JWT tokens expire after 30 minutes (configurable)
- Tokens are stored in localStorage (for demo)
- HTTPS required for production
- Environment variables never committed to git
- Google OAuth provides additional security layer

## Files Modified

### Frontend
- `src/context/AuthContext.js` - Fixed process.env usage, added Google auth handler
- `src/components/Auth/GoogleSignIn.js` - New component for Google Sign-In
- `src/components/Auth/LoginForm.js` - Added Google Sign-In button
- `src/components/Auth/SignupForm.js` - Added Google Sign-In button
- `src/components/Auth/Auth.module.css` - Added Google button styles

### Backend
- `app/routers/auth.py` - Added `/google` endpoint for OAuth token verification

## Testing

To test authentication:
1. Open the site
2. Click the chat button
3. Try signing up with email/password
4. Verify chat opens after login
5. Check localStorage for auth token
6. Refresh page - should remain logged in
7. Try logging out and back in