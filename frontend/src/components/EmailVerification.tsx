/**
 * Email verification component
 */

import React, { useState, useEffect, useCallback } from 'react';
import { authApi } from '../services/api';

interface EmailVerificationProps {
  email?: string;
  onVerificationComplete?: () => void;
  onBack?: () => void;
}

export const EmailVerification: React.FC<EmailVerificationProps> = ({
  email,
  onVerificationComplete,
  onBack,
}) => {
  const [isResending, setIsResending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [verificationToken, setVerificationToken] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const handleVerifyEmail = useCallback(async (token: string) => {
    setIsVerifying(true);
    setError(null);
    setMessage(null);

    try {
      const response = await authApi.verifyEmail(token);
      setMessage(response.message);
      
      // Clear the token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // Call completion callback after a short delay
      setTimeout(() => {
        if (onVerificationComplete) {
          onVerificationComplete();
        }
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Email verification failed');
    } finally {
      setIsVerifying(false);
    }
  }, [onVerificationComplete]);

  // Check for verification token in URL on component mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      setVerificationToken(token);
      handleVerifyEmail(token);
    }
  }, [handleVerifyEmail]);

  const handleResendVerification = async () => {
    if (!email) {
      setError('Email address is required to resend verification');
      return;
    }

    setIsResending(true);
    setError(null);
    setMessage(null);

    try {
      const response = await authApi.resendVerification(email);
      setMessage(response.message);
    } catch (err: any) {
      setError(err.message || 'Failed to resend verification email');
    } finally {
      setIsResending(false);
    }
  };

  // If we're verifying a token
  if (verificationToken) {
    return (
      <div className="email-verification">
        <div className="verification-header">
          <h2>🎨 Email Verification</h2>
        </div>

        {isVerifying && (
          <div className="verification-loading">
            <div className="loading-spinner"></div>
            <p>Verifying your email address...</p>
            <p className="loading-subtext">Please wait while we confirm your email.</p>
          </div>
        )}

        {message && (
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h3>Email Verified Successfully!</h3>
            <p>{message}</p>
            <p>You can now log in to your account and start tracking your miniatures!</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <div className="error-icon">❌</div>
            <h3>Verification Failed</h3>
            <p>{error}</p>
            <div className="error-help">
              <h4>What can you do?</h4>
              <ul>
                <li>The verification link may have expired (links expire after 24 hours)</li>
                <li>The link may have already been used</li>
                <li>Try requesting a new verification email below</li>
                <li>Contact support if the problem persists</li>
              </ul>
            </div>
            {email && (
              <div className="resend-section">
                <button
                  type="button"
                  onClick={handleResendVerification}
                  disabled={isResending}
                  className="btn-primary"
                >
                  {isResending ? 'Sending...' : 'Send New Verification Email'}
                </button>
              </div>
            )}
          </div>
        )}

        <div className="form-actions">
          {message && (
            <button type="button" onClick={onBack} className="btn-primary">
              Continue to Login
            </button>
          )}
          {!message && (
            <button type="button" onClick={onBack} className="btn-secondary">
              Back to Login
            </button>
          )}
        </div>
      </div>
    );
  }

  // Default verification pending view
  return (
    <div className="email-verification">
      <div className="verification-header">
        <h2>Check Your Email</h2>
        <p>We've sent a verification link to your email address.</p>
      </div>

      <div className="verification-instructions">
        <div className="instruction-step">
          <span className="step-number">1</span>
          <p>Check your email inbox (and spam folder)</p>
        </div>
        <div className="instruction-step">
          <span className="step-number">2</span>
          <p>Click the verification link in the email</p>
        </div>
        <div className="instruction-step">
          <span className="step-number">3</span>
          <p>Return here to log in to your account</p>
        </div>
      </div>

      {email && (
        <div className="email-display">
          <p>Verification email sent to: <strong>{email}</strong></p>
        </div>
      )}

      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="verification-actions">
        <button type="button" onClick={onBack} className="btn-primary">
          Back to Login
        </button>
        
        {email && (
          <button
            type="button"
            onClick={handleResendVerification}
            disabled={isResending}
            className="btn-secondary"
          >
            {isResending ? 'Sending...' : 'Resend Verification Email'}
          </button>
        )}
      </div>

      <div className="verification-help">
        <h4>Didn't receive the email?</h4>
        <ul>
          <li>Check your spam or junk folder</li>
          <li>Make sure you entered the correct email address</li>
          <li>Wait a few minutes - emails can sometimes be delayed</li>
          <li>Try resending the verification email</li>
        </ul>
      </div>
    </div>
  );
}; 