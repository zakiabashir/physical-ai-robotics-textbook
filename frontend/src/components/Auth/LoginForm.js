import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import GoogleSignIn from './GoogleSignIn';
import styles from './Auth.module.css';

const LoginForm = ({ onToggleMode }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, googleSignIn } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(username, password);

    if (!result.success) {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <h2 className={styles.authTitle}>Sign In</h2>
        <p className={styles.authSubtitle}>
          Access your personalized learning experience
        </p>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          {error && (
            <div className={styles.errorMessage}>
              {error}
            </div>
          )}

          <div className={styles.formGroup}>
            <label htmlFor="username" className={styles.formLabel}>
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.formInput}
              placeholder="Enter your username"
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.formLabel}>
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.formInput}
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`${styles.authButton} ${loading ? styles.loading : ''}`}
          >
            {loading ? 'Signing In...' : 'Sign In'}
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
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onToggleMode}
              className={styles.linkButton}
            >
              Sign Up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;