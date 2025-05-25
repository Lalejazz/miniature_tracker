/**
 * Login form component
 */

import React, { useState } from 'react';
import { LoginRequest } from '../types';

interface LoginFormProps {
  onLogin: (credentials: LoginRequest) => Promise<void>;
  onSwitchToRegister: () => void;
  onForgotPassword: () => void;
  isLoading: boolean;
  error: string | null;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onLogin,
  onSwitchToRegister,
  onForgotPassword,
  isLoading,
  error,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onLogin({ email, password });
  };

  return (
    <div className="auth-form">
      <h2>Login to Miniature Tracker</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
            placeholder="your.email@example.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Enter your password"
            minLength={6}
          />
        </div>

        <div className="forgot-password-link">
          <button 
            type="button" 
            className="link-button" 
            onClick={onForgotPassword}
            disabled={isLoading}
          >
            Forgot your password?
          </button>
        </div>

        <button 
          type="submit" 
          className="auth-button"
          disabled={isLoading}
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p className="auth-switch">
        Don't have an account?{' '}
        <button 
          type="button" 
          className="link-button" 
          onClick={onSwitchToRegister}
          disabled={isLoading}
        >
          Register here
        </button>
      </p>
    </div>
  );
}; 