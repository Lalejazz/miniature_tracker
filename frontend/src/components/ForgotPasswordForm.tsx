import React, { useState } from 'react';
import { authApi } from '../services/api';
import { PasswordResetRequest } from '../types';

interface ForgotPasswordFormProps {
  onBack: () => void;
}

const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({ onBack }) => {
  const [formData, setFormData] = useState<PasswordResetRequest>({
    email: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await authApi.forgotPassword(formData);
      setMessage(response.message);
      setIsSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Failed to send password reset email');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (isSubmitted) {
    return (
      <div className="forgot-password-form">
        <div className="forgot-password-header">
          <h2>Check Your Email</h2>
        </div>

        <div className="success-message">
          <p>{message}</p>
          <p>Please check your email for a password reset link. The link will expire in 1 hour.</p>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onBack} className="btn-secondary">
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="forgot-password-form">
      <div className="forgot-password-header">
        <h2>Reset Your Password</h2>
        <p>Enter your email address and we'll send you a link to reset your password.</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            disabled={isLoading}
            placeholder="Enter your email address"
          />
        </div>

        <div className="form-actions">
          <button
            type="submit"
            disabled={isLoading || !formData.email.trim()}
            className="btn-primary"
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
          <button
            type="button"
            onClick={onBack}
            className="btn-secondary"
            disabled={isLoading}
          >
            Back to Login
          </button>
        </div>
      </form>
    </div>
  );
};

export default ForgotPasswordForm; 