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
      <div className={`space-y-3 ${className}`}>
        <div className="h-10 bg-gray-200 rounded animate-pulse"></div>
      </div>
    );
  }

  if (!config || !config.google_enabled) {
    return null; // Google OAuth not configured
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <button
        onClick={handleGoogleLogin}
        className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
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
        Continue with Google
      </button>
    </div>
  );
};

export default OAuthLogin; 