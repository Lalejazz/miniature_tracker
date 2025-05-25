/**
 * Register form component
 */

import React, { useState } from 'react';
import { UserCreate } from '../types';
import { TermsAndConditions } from './TermsAndConditions';

interface RegisterFormProps {
  onRegister: (userData: UserCreate) => Promise<void>;
  onSwitchToLogin: () => void;
  isLoading: boolean;
  error: string | null;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({
  onRegister,
  onSwitchToLogin,
  isLoading,
  error,
}) => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [showTerms, setShowTerms] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    if (!acceptTerms) {
      alert('You must accept the terms and conditions to register');
      return;
    }

    await onRegister({ 
      email, 
      username, 
      password, 
      accept_terms: acceptTerms 
    });
  };

  const handleTermsAccept = () => {
    setAcceptTerms(true);
    setShowTerms(false);
  };

  const handleTermsDecline = () => {
    setAcceptTerms(false);
    setShowTerms(false);
  };

  if (showTerms) {
    return (
      <div className="auth-form">
        <TermsAndConditions
          isModal={true}
          onAccept={handleTermsAccept}
          onDecline={handleTermsDecline}
          showButtons={true}
        />
      </div>
    );
  }

  return (
    <div className="auth-form">
      <h2>Register for Miniature Tracker</h2>
      
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
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Choose a username"
            minLength={3}
            maxLength={50}
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
            placeholder="Enter a password (min 8 characters)"
            minLength={8}
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password:</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            disabled={isLoading}
            placeholder="Confirm your password"
            minLength={8}
          />
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
              disabled={isLoading}
            />
            <span>
              I accept the{' '}
              <button
                type="button"
                className="link-button"
                onClick={() => setShowTerms(true)}
                disabled={isLoading}
              >
                Terms and Conditions
              </button>
            </span>
          </label>
        </div>

        <button 
          type="submit" 
          className="auth-button"
          disabled={isLoading || !acceptTerms}
        >
          {isLoading ? 'Registering...' : 'Register'}
        </button>
      </form>

      <p className="auth-switch">
        Already have an account?{' '}
        <button 
          type="button" 
          className="link-button" 
          onClick={onSwitchToLogin}
          disabled={isLoading}
        >
          Login here
        </button>
      </p>
    </div>
  );
}; 