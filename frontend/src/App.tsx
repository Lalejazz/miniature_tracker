import React, { useState, useEffect } from 'react';
import './App.css';
import { Miniature, MiniatureCreate, UserCreate, LoginRequest } from './types';
import { miniatureApi, authApi, tokenManager } from './services/api';
import MiniatureList from './components/MiniatureList';
import MiniatureForm from './components/MiniatureForm';
import { LoginForm } from './components/LoginForm';
import { RegisterForm } from './components/RegisterForm';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import { UserHeader } from './components/UserHeader';
import Changelog from './components/Changelog';

type AuthMode = 'login' | 'register' | 'forgot-password' | 'reset-password';

interface AuthState {
  user: any | null;
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

  // UI state
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);
  
  // Tab state
  const [currentTab, setCurrentTab] = useState<'miniatures' | 'changelog'>('miniatures');

  // Miniature state
  const [miniatures, setMiniatures] = useState<Miniature[]>([]);
  const [miniaturesLoading, setMiniaturesLoading] = useState(false);
  const [miniaturesError, setMiniaturesError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // Check for password reset token in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      setResetToken(token);
      setAuthMode('reset-password');
      // Clear the URL parameter for security
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // Check for existing token on mount
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
        } catch (err) {
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

  // Load miniatures when authenticated
  useEffect(() => {
    if (authState.isAuthenticated) {
      loadMiniatures();
    }
  }, [authState.isAuthenticated]);

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
      setAuthError(err.message || 'Login failed');
      setAuthState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleRegister = async (userData: UserCreate) => {
    try {
      setAuthError(null);
      setAuthState(prev => ({ ...prev, isLoading: true }));

      await authApi.register(userData);
      
      // Auto-login after registration
      await handleLogin({ email: userData.email, password: userData.password });
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
  };

  const handlePasswordResetSuccess = () => {
    setAuthSuccess('Password has been reset successfully! You can now log in with your new password.');
    setAuthMode('login');
    setResetToken(null);
  };

  const handlePasswordResetError = (error: string) => {
    setAuthError(error);
    setAuthMode('login');
    setResetToken(null);
  };

  const clearMessages = () => {
    setAuthError(null);
    setAuthSuccess(null);
  };

  const loadMiniatures = async () => {
    try {
      setMiniaturesLoading(true);
      setMiniaturesError(null);
      const data = await miniatureApi.getAll();
      setMiniatures(data);
    } catch (err: any) {
      setMiniaturesError(err.message || 'Failed to load miniatures');
      console.error('Error loading miniatures:', err);
    } finally {
      setMiniaturesLoading(false);
    }
  };

  const handleCreateMiniature = async (miniatureData: MiniatureCreate) => {
    try {
      setMiniaturesError(null);
      const newMiniature = await miniatureApi.create(miniatureData);
      setMiniatures(prev => [...prev, newMiniature]);
      setShowForm(false);
    } catch (err: any) {
      setMiniaturesError(err.message || 'Failed to create miniature');
      console.error('Error creating miniature:', err);
    }
  };

  const handleUpdateMiniature = async (id: string, updates: Partial<Miniature>) => {
    try {
      setMiniaturesError(null);
      const updated = await miniatureApi.update(id, updates);
      setMiniatures(prev => 
        prev.map(m => m.id === id ? updated : m)
      );
    } catch (err: any) {
      setMiniaturesError(err.message || 'Failed to update miniature');
      console.error('Error updating miniature:', err);
    }
  };

  const handleMiniatureUpdate = (updatedMiniature: Miniature) => {
    setMiniatures(prev => 
      prev.map(m => m.id === updatedMiniature.id ? updatedMiniature : m)
    );
  };

  const handleDeleteMiniature = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this miniature?')) {
      return;
    }

    try {
      setMiniaturesError(null);
      await miniatureApi.delete(id);
      setMiniatures(prev => prev.filter(m => m.id !== id));
    } catch (err: any) {
      setMiniaturesError(err.message || 'Failed to delete miniature');
      console.error('Error deleting miniature:', err);
    }
  };

  // Show loading spinner during initial auth check
  if (authState.isLoading) {
    return (
      <div className="App">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  // Show authentication forms if not logged in
  if (!authState.isAuthenticated) {
    return (
      <div className="App">
        <div className="auth-container">
          {authSuccess && (
            <div className="success-message">
              {authSuccess}
            </div>
          )}
          
          {authError && (
            <div className="error-message">
              {authError}
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
            />
          )}
        </div>
      </div>
    );
  }

  // Show main app for authenticated users
  return (
    <div className="App">
      <header className="App-header">
        <h1>🎨 Miniature Tracker</h1>
        <p>Track your Warhammer miniature collection and painting progress</p>
      </header>

      <main className="App-main">
        <UserHeader user={authState.user!} onLogout={handleLogout} />

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-button ${currentTab === 'miniatures' ? 'active' : ''}`}
            onClick={() => setCurrentTab('miniatures')}
          >
            🎨 My Miniatures
          </button>
          <button 
            className={`tab-button ${currentTab === 'changelog' ? 'active' : ''}`}
            onClick={() => setCurrentTab('changelog')}
          >
            📋 Changelog
          </button>
        </div>

        {/* Tab Content */}
        {currentTab === 'miniatures' && (
          <>
            {miniaturesError && (
              <div className="error-banner">
                <span>⚠️ {miniaturesError}</span>
                <button onClick={() => setMiniaturesError(null)}>✕</button>
              </div>
            )}

            <div className="controls">
              <button 
                className="add-button"
                onClick={() => setShowForm(!showForm)}
              >
                {showForm ? '✕ Cancel' : '+ Add Miniature'}
              </button>
              <button 
                className="refresh-button"
                onClick={loadMiniatures}
                disabled={miniaturesLoading}
              >
                🔄 Refresh
              </button>
            </div>

            {showForm && (
              <MiniatureForm
                onSubmit={handleCreateMiniature}
                onCancel={() => setShowForm(false)}
              />
            )}

            {miniaturesLoading ? (
              <div className="loading">Loading miniatures...</div>
            ) : (
              <MiniatureList
                miniatures={miniatures}
                onUpdate={handleUpdateMiniature}
                onDelete={handleDeleteMiniature}
                onMiniatureUpdate={handleMiniatureUpdate}
              />
            )}
          </>
        )}

        {currentTab === 'changelog' && <Changelog />}
      </main>

      <footer className="App-footer">
        <p>Built with React + FastAPI | {miniatures.length} miniatures tracked</p>
      </footer>
    </div>
  );
}

export default App; 