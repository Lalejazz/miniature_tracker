import React, { useState, useEffect } from 'react';

// API_BASE_URL definition (same as in api.ts)
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Will use same domain in production
  : 'http://127.0.0.1:8000'; // Local development

interface OAuthConfig {
  google_enabled: boolean;
}

interface OAuthLoginProps {
  onSuccess?: (token: string) => void;
  className?: string;
}

const OAuthLogin: React.FC<OAuthLoginProps> = ({ onSuccess, className = '' }) => {
  const [config, setConfig] = useState<OAuthConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load OAuth configuration
    const loadConfig = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/oauth/config`);
        if (response.ok) {
          const oauthConfig = await response.json();
          setConfig(oauthConfig);
        }
      } catch (error) {
        console.error('Failed to load OAuth config:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadConfig();

    // Check for OAuth token in URL (from redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');

    if (token && onSuccess) {
      // Clear the URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
      onSuccess(token);
    } else if (error) {
      console.error('OAuth error:', error);
      // You could show an error message here
    }
  }, [onSuccess]);

  const handleGoogleLogin = () => {
    // Redirect to Google OAuth login endpoint
    window.location.href = `${API_BASE_URL}/auth/oauth/google/login`;
  };

  if (isLoading) {
    return (
      <div className={`oauth-loading ${className}`}>
        <div className="oauth-skeleton"></div>
      </div>
    );
  }

  if (!config || !config.google_enabled) {
    return null; // Google OAuth not configured
  }

  return (
    <div className={`oauth-container ${className}`}>
      <button
        onClick={handleGoogleLogin}
        className="google-oauth-button"
      >
        <div className="google-icon">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" clipRule="evenodd" d="M17.64 9.20454C17.64 8.56636 17.5827 7.95272 17.4764 7.36363H9V10.8445H13.8436C13.635 11.9699 13.0009 12.9231 12.0477 13.5613V15.8195H14.9564C16.6582 14.2527 17.64 11.9454 17.64 9.20454Z" fill="#4285F4"/>
            <path fillRule="evenodd" clipRule="evenodd" d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5613C11.2418 14.1013 10.2109 14.4204 9 14.4204C6.65591 14.4204 4.67182 12.8372 3.96409 10.71H0.957275V13.0418C2.43818 15.9831 5.48182 18 9 18Z" fill="#34A853"/>
            <path fillRule="evenodd" clipRule="evenodd" d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957273C0.347727 6.17318 0 7.54772 0 9C0 10.4523 0.347727 11.8268 0.957273 13.0418L3.96409 10.71Z" fill="#FBBC05"/>
            <path fillRule="evenodd" clipRule="evenodd" d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65591 3.57955 9 3.57955Z" fill="#EA4335"/>
          </svg>
        </div>
        <span className="google-text">Continue with Google</span>
      </button>
    </div>
  );
};

export default OAuthLogin; 