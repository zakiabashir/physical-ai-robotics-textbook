import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import GoogleSignIn from './GoogleSignIn';
import styles from './Auth.module.css';

const SignupForm = ({ onToggleMode }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, login, googleSignIn } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    // Register the user
    const registerResult = await register(username, password, email);

    if (!registerResult.success) {
      setError(registerResult.error);
      setLoading(false);
      return;
    }

    // Auto-login after successful registration
    const loginResult = await login(username, password);

    if (!loginResult.success) {
      setError('Registration successful, but login failed. Please try logging in manually.');
    }

    setLoading(false);
  };

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <h2 className={styles.authTitle}>Sign Up</h2>
        <p className={styles.authSubtitle}>
          Create your account to start learning
        </p>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          {error && (
            <div className={styles.errorMessage}>
              {error}
            </div>
          )}

          <div className={styles.formGroup}>
            <label htmlFor="username" className={styles.formLabel}>
              Username *
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.formInput}
              placeholder="Choose a username"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.formLabel}>
              Email (optional)
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={styles.formInput}
              placeholder="your@email.com"
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.formLabel}>
              Password *
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.formInput}
              placeholder="Create a password (min 6 chars)"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="confirmPassword" className={styles.formLabel}>
              Confirm Password *
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={styles.formInput}
              placeholder="Confirm your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`${styles.authButton} ${loading ? styles.loading : ''}`}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className={styles.divider}>
          <span>OR</span>
        </div>

        <GoogleSignIn
          onSuccess={() => {
            // Success is handled by GoogleSignIn component
          }}
          onError={(errorMessage) => {
            setError(errorMessage);
          }}
        />

        <div className={styles.authFooter}>
          <p>
            Already have an account?{' '}
            <button
              type="button"
              onClick={onToggleMode}
              className={styles.linkButton}
            >
              Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupForm;