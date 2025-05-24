import React, { useState, useEffect } from 'react';
import { authApi } from '../services/api';
import { PasswordReset } from '../types';

interface ResetPasswordFormProps {
  token: string;
  onSuccess: () => void;
  onError: (error: string) => void;
}

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
  token,
  onSuccess,
  onError
}) => {
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    // Validate token format
    if (!token || token.length !== 32) {
      onError('Invalid reset token. Please request a new password reset.');
    }
  }, [token, onError]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const resetRequest: PasswordReset = {
        token,
        new_password: formData.password
      };

      await authApi.resetPassword(resetRequest);
      onSuccess();
    } catch (err: any) {
      onError(err.message || 'Failed to reset password');
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

    // Clear field-specific error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  return (
    <div className="reset-password-form">
      <div className="reset-password-header">
        <h2>Set New Password</h2>
        <p>Enter your new password below.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="password">New Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Enter new password"
            minLength={8}
          />
          {errors.password && (
            <div className="field-error">{errors.password}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm New Password</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Confirm new password"
            minLength={8}
          />
          {errors.confirmPassword && (
            <div className="field-error">{errors.confirmPassword}</div>
          )}
        </div>

        <div className="password-requirements">
          <p>Password must be at least 8 characters long.</p>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            disabled={isLoading || !formData.password || !formData.confirmPassword}
            className="btn-primary"
          >
            {isLoading ? 'Resetting Password...' : 'Reset Password'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ResetPasswordForm; 