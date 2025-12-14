import React, { useState, useEffect } from 'react';
import styles from './Auth.module.css';

const GoogleSignIn = ({ onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    onError(''); // Clear any previous errors

    // Google Sign-In is not configured yet
    // This prevents the script loading error
    initializeGoogleSignIn();
  };

  const initializeGoogleSignIn = () => {
    try {
      // Note: Google Sign-In requires proper OAuth configuration
      // For production, you need to:
      // 1. Create a Google Cloud Console project
      // 2. Create OAuth 2.0 credentials
      // 3. Add your domain to authorized origins
      // 4. Replace the placeholder client ID

      onError('Google Sign-In is not configured. Please use email/password to sign up or sign in.');
      setLoading(false);

      // Uncomment and configure when you have a valid client ID:
      /*
      window.google.accounts.id.initialize({
        client_id: 'YOUR_VALID_GOOGLE_CLIENT_ID_HERE',
        callback: handleCredentialResponse,
        auto_select: false,
      });

      // Show the Google Sign-In popup
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // Fallback to manual sign-in button
        }
      });
      */
    } catch (error) {
      onError('Google Sign-In is currently unavailable. Please use email/password.');
      setLoading(false);
    }
  };

  const handleCredentialResponse = async (response) => {
    try {
      // Send the credential to our backend
      const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app';
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: response.credential,
        }),
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Google authentication failed');
      }

      const data = await res.json();

      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to get user info');
      }

      const userData = await userResponse.json();

      // Store token and user
      localStorage.setItem('authToken', data.access_token);
      localStorage.setItem('authUser', JSON.stringify(userData));

      // Trigger page reload to update auth state
      window.location.reload();
    } catch (error) {
      console.error('Google auth error:', error);
      onError(error.message || 'Google Sign-In failed. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className={styles.googleSignInContainer}>
      <button
        type="button"
        onClick={handleGoogleSignIn}
        disabled={loading}
        className={`${styles.googleSignInButton} ${loading ? styles.loading : ''}`}
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          style={{ marginRight: '8px' }}
        >
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
        {loading ? 'Connecting...' : 'Continue with Google (Coming Soon)'}
      </button>
    </div>
  );
};

// Google Sign-In script will be loaded when properly configured
// This prevents errors from invalid client IDs

export default GoogleSignIn;