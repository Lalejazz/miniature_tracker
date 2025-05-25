import React, { useState, useEffect } from 'react';
import './App.css';
import { Miniature, MiniatureCreate, UserCreate, LoginRequest, UserPreferences } from './types';
import { miniatureApi, authApi, tokenManager, playerApi } from './services/api';
import MiniatureList from './components/MiniatureList';
import UnitForm from './components/UnitForm';
import Statistics from './components/Statistics';
import { LoginForm } from './components/LoginForm';
import { RegisterForm } from './components/RegisterForm';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import { EmailVerification } from './components/EmailVerification';
import { UserHeader } from './components/UserHeader';
import Changelog from './components/Changelog';
import UserPreferencesForm from './components/UserPreferencesForm';
import PlayerSearch from './components/PlayerSearch';
import ImportExport from './components/ImportExport';

type AuthMode = 'login' | 'register' | 'forgot-password' | 'reset-password' | 'email-verification';
type Tab = 'units' | 'statistics' | 'changelog' | 'preferences' | 'players' | 'import-export';

interface AuthState {
  user: any;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

function App() {
  // Authentication state
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState<string | null>(null);

  // App state
  const [miniatures, setMiniatures] = useState<Miniature[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingMiniature, setEditingMiniature] = useState<Miniature | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('units');
  const [miniaturesError, setMiniaturesError] = useState<string | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);

  // Check for existing token on app load
  useEffect(() => {
    const checkAuth = async () => {
      const token = tokenManager.getToken();
      if (token) {
        try {
          const user = await authApi.getCurrentUser();
          setAuthState({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // Token is invalid, clear it
          tokenManager.clearToken();
          setAuthState({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } else {
        setAuthState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    checkAuth();
  }, []);

  // Check for tokens in URL and determine the correct mode
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const currentPath = window.location.pathname;
    
    if (token) {
      // Determine the mode based on the URL path
      if (currentPath.includes('/verify-email')) {
        // This is an email verification link
        setAuthMode('email-verification');
        // Don't clear the token yet - let EmailVerification component handle it
      } else if (currentPath.includes('/reset-password')) {
        // This is a password reset link
        setResetToken(token);
        setAuthMode('reset-password');
        // Clear the token from URL for security
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        // Default behavior - check token length to guess the type
        // Email verification tokens are typically longer than password reset tokens
        if (token.length > 32) {
          setAuthMode('email-verification');
        } else {
          setResetToken(token);
          setAuthMode('reset-password');
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      }
    }
  }, []);

  // Load miniatures when authenticated
  useEffect(() => {
    if (authState.isAuthenticated) {
      loadMiniatures();
      loadUserPreferences();
    }
  }, [authState.isAuthenticated]);

  const loadMiniatures = async () => {
    try {
      setMiniaturesError(null);
      const data = await miniatureApi.getAll();
      setMiniatures(data);
    } catch (error: any) {
      setMiniaturesError(error.message || 'Failed to load miniatures');
    }
  };

  const loadUserPreferences = async () => {
    try {
      const preferences = await playerApi.getPreferences();
      setUserPreferences(preferences);
    } catch (error) {
      // User preferences might not exist yet, that's okay
      setUserPreferences(null);
    }
  };

  const handleLogin = async (credentials: LoginRequest) => {
    try {
      setAuthError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const tokenResponse = await authApi.login(credentials);
      tokenManager.setToken(tokenResponse.access_token);

      const user = await authApi.getCurrentUser();
      setAuthState({
        user,
        token: tokenResponse.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: any) {
      // Check if the error is about email verification
      if (err.message && err.message.includes('verify your email')) {
        setPendingVerificationEmail(credentials.email);
        setAuthMode('email-verification');
        setAuthError('Please verify your email address before logging in. Check your email for a verification link.');
      } else {
        setAuthError(err.message || 'Login failed');
      }
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleRegister = async (userData: UserCreate) => {
    try {
      setAuthError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));

      const response = await authApi.register(userData);
      
      // Registration successful, show email verification
      setPendingVerificationEmail(userData.email);
      setAuthMode('email-verification');
      setAuthSuccess(response.message);
      setAuthState(prev => ({ ...prev, isLoading: false }));
    } catch (err: any) {
      setAuthError(err.message || 'Registration failed');
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleLogout = () => {
    authApi.logout();
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
    setMiniatures([]);
    setShowForm(false);
    setMiniaturesError(null);
    setUserPreferences(null);
  };

  const handlePasswordResetSuccess = () => {
    setAuthSuccess('Password has been reset successfully! You can now log in with your new password.');
    setAuthMode('login');
    setResetToken(null);
  };

  const handlePasswordResetError = (error: string) => {
    setAuthError(error);
    setAuthState(prev => ({ ...prev, isLoading: false }));
  };

  const handleEmailVerificationComplete = () => {
    setAuthSuccess('Email verified successfully! You can now log in.');
    setAuthMode('login');
    setPendingVerificationEmail(null);
  };

  const clearMessages = () => {
    setAuthError(null);
    setAuthSuccess(null);
  };

  const handleCreateMiniature = async (miniatureData: MiniatureCreate) => {
    try {
      const newMiniature = await miniatureApi.create(miniatureData);
      setMiniatures(prev => [...prev, newMiniature]);
      setShowForm(false);
    } catch (error: any) {
      setMiniaturesError(error.message || 'Failed to create miniature');
    }
  };

  const handleUpdateMiniature = async (id: string, updates: any) => {
    try {
      const updatedMiniature = await miniatureApi.update(id, updates);
      setMiniatures(prev => 
        prev.map(m => m.id === id ? updatedMiniature : m)
      );
      setEditingMiniature(null);
    } catch (error: any) {
      setMiniaturesError(error.message || 'Failed to update miniature');
    }
  };

  const handleDeleteMiniature = async (id: string) => {
    try {
      await miniatureApi.delete(id);
      setMiniatures(prev => prev.filter(m => m.id !== id));
    } catch (error: any) {
      setMiniaturesError(error.message || 'Failed to delete miniature');
    }
  };

  const handleImportComplete = () => {
    loadMiniatures(); // Reload miniatures after import
  };

  // Show loading spinner during initial auth check
  if (authState.isLoading && !authState.isAuthenticated) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication forms if not authenticated
  if (!authState.isAuthenticated) {
    return (
      <div className="app">
        <div className="auth-container">
          {authSuccess && (
            <div className="success-message">
              {authSuccess}
            </div>
          )}

          {authMode === 'login' && (
            <LoginForm
              onLogin={handleLogin}
              onSwitchToRegister={() => {
                setAuthMode('register');
                clearMessages();
              }}
              onForgotPassword={() => {
                setAuthMode('forgot-password');
                clearMessages();
              }}
              isLoading={authState.isLoading}
              error={authError}
            />
          )}

          {authMode === 'register' && (
            <RegisterForm
              onRegister={handleRegister}
              onSwitchToLogin={() => {
                setAuthMode('login');
                clearMessages();
              }}
              isLoading={authState.isLoading}
              error={authError}
            />
          )}

          {authMode === 'forgot-password' && (
            <ForgotPasswordForm
              onBack={() => {
                setAuthMode('login');
                clearMessages();
              }}
            />
          )}

          {authMode === 'reset-password' && resetToken && (
            <ResetPasswordForm
              token={resetToken}
              onSuccess={handlePasswordResetSuccess}
              onError={handlePasswordResetError}
              onBack={() => {
                setAuthMode('login');
                setResetToken(null);
                clearMessages();
              }}
            />
          )}

          {authMode === 'email-verification' && (
            <EmailVerification
              email={pendingVerificationEmail || undefined}
              onVerificationComplete={handleEmailVerificationComplete}
              onBack={() => {
                setAuthMode('login');
                setPendingVerificationEmail(null);
                clearMessages();
              }}
            />
          )}
        </div>
      </div>
    );
  }

  // Main authenticated app
  return (
    <div className="app">
      <UserHeader 
        user={authState.user} 
        onLogout={handleLogout}
      />

      <nav className="main-nav">
        <button 
          className={activeTab === 'units' ? 'active' : ''}
          onClick={() => setActiveTab('units')}
        >
          My Units
        </button>
        <button 
          className={activeTab === 'statistics' ? 'active' : ''}
          onClick={() => setActiveTab('statistics')}
        >
          Statistics
        </button>
        <button 
          className={activeTab === 'players' ? 'active' : ''}
          onClick={() => setActiveTab('players')}
        >
          Player Search
        </button>
        <button 
          className={activeTab === 'preferences' ? 'active' : ''}
          onClick={() => setActiveTab('preferences')}
        >
          User Preferences
        </button>
        <button 
          className={activeTab === 'import-export' ? 'active' : ''}
          onClick={() => setActiveTab('import-export')}
        >
          Import/Export
        </button>
        <button 
          className={activeTab === 'changelog' ? 'active' : ''}
          onClick={() => setActiveTab('changelog')}
        >
          Changelog
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'units' && (
          <>
            {miniaturesError && (
              <div className="error-message">
                {miniaturesError}
                <button onClick={() => setMiniaturesError(null)}>×</button>
              </div>
            )}

            <div className="units-header">
              <h2>My Miniature Collection</h2>
              <button 
                className="add-button"
                onClick={() => setShowForm(true)}
              >
                + Add Unit
              </button>
            </div>

            {showForm && (
              <UnitForm
                onSubmit={handleCreateMiniature}
                onCancel={() => setShowForm(false)}
              />
            )}

            {editingMiniature && (
              <UnitForm
                miniature={editingMiniature}
                onSubmit={(data) => handleUpdateMiniature(editingMiniature.id, data)}
                onCancel={() => setEditingMiniature(null)}
                isEditing={true}
              />
            )}

            <MiniatureList
              miniatures={miniatures}
              onEdit={setEditingMiniature}
              onDelete={handleDeleteMiniature}
            />
          </>
        )}

        {activeTab === 'statistics' && (
          <Statistics onError={setMiniaturesError} />
        )}

        {activeTab === 'players' && (
          <PlayerSearch userHasPreferences={userPreferences !== null} />
        )}

        {activeTab === 'preferences' && (
          <UserPreferencesForm
            existingPreferences={userPreferences}
            onSave={loadUserPreferences}
          />
        )}

        {activeTab === 'import-export' && (
          <ImportExport onImportComplete={handleImportComplete} />
        )}

        {activeTab === 'changelog' && (
          <Changelog />
        )}
      </main>
    </div>
  );
}

export default App; 