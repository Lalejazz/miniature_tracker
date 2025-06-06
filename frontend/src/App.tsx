import React, { useState, useEffect } from 'react';
import './App.css';
import './themes.css';
import { Miniature, MiniatureCreate, UserCreate, LoginRequest, UserPreferences, Theme } from './types';
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
import UserPreferencesForm from './components/UserPreferencesForm';
import { FeedbackForm } from './components/FeedbackForm';
import PlayerSearch from './components/PlayerSearch';
import Changelog from './components/Changelog';
import Projects from './components/Projects';
import { ThemeProvider } from './contexts/ThemeContext';

type AuthMode = 'login' | 'register' | 'forgot-password' | 'reset-password' | 'email-verification';
type Tab = 'units' | 'statistics' | 'projects' | 'preferences' | 'players' | 'changelog';

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
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  // Handle user preferences save
  const handleUserPreferencesSave = async (preferences: UserPreferences) => {
    setUserPreferences(preferences);
    
    // If theme changed, update the theme context
    if (preferences.theme) {
      // The theme context will be updated through the ThemeProvider
      // which watches for changes in the initialTheme prop
    }
    
    // Don't redirect to units tab - let user stay on preferences to see their updates
  };

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
      
      // Update theme if preferences have a theme set
      if (preferences?.theme) {
        // The ThemeProvider will handle the actual theme application
        // We just need to make sure the theme context is updated
      }
    } catch (error) {
      console.log('No user preferences found or error loading preferences');
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
    console.log('handleUpdateMiniature called with:', { id, updates });
    try {
      const updatedMiniature = await miniatureApi.update(id, updates);
      console.log('API update successful:', updatedMiniature);
      
      // Update the miniatures list
      setMiniatures(prev => {
        console.log('Current miniatures before update:', prev.map(m => ({ id: m.id, name: m.name, status: m.status, quantity: m.quantity })));
        const newMiniatures = prev.map(m => m.id === id ? updatedMiniature : m);
        console.log('New miniatures array:', newMiniatures.map(m => ({ id: m.id, name: m.name, status: m.status, quantity: m.quantity })));
        return newMiniatures;
      });
      
      // Update the editing miniature state with fresh data from API
      setEditingMiniature(updatedMiniature);
      console.log('Updated editingMiniature with fresh API data:', updatedMiniature);
      
      // Close the edit form after a brief delay to show the updated values
      setTimeout(() => {
        setEditingMiniature(null);
        console.log('Form closed after showing updated values');
      }, 100);
      
    } catch (error: any) {
      console.error('Update failed:', error);
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
    <ThemeProvider initialTheme={userPreferences?.theme || Theme.BLUE_GRADIENT}>
      <div className="app">
        <header className="App-header">
          <h1>🎨 Miniature Tracker</h1>
          <p>Track your miniature painting progress and connect with fellow hobbyists</p>
        </header>

        <UserHeader 
          user={authState.user} 
          onLogout={handleLogout}
        />

        <nav className="main-nav">
          <button 
            className={activeTab === 'units' ? 'active' : ''}
            onClick={() => setActiveTab('units')}
          >
            🎨 My Units
          </button>
          <button 
            className={activeTab === 'statistics' ? 'active' : ''}
            onClick={() => setActiveTab('statistics')}
          >
            📊 Statistics
          </button>
          <button 
            className={activeTab === 'projects' ? 'active' : ''}
            onClick={() => setActiveTab('projects')}
          >
            📅 Projects
          </button>
          <button 
            className={activeTab === 'players' ? 'active' : ''}
            onClick={() => setActiveTab('players')}
          >
            🔍 Player Search
          </button>
          <button 
            className={activeTab === 'preferences' ? 'active' : ''}
            onClick={() => setActiveTab('preferences')}
          >
            ⚙️ User Preferences
          </button>
        </nav>

        <main className="App-main">
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
                onRefresh={loadMiniatures}
              />
            </>
          )}

          {activeTab === 'statistics' && (
            <Statistics onError={setMiniaturesError} />
          )}

          {activeTab === 'projects' && (
            <Projects onError={setMiniaturesError} />
          )}

          {activeTab === 'preferences' && (
            <UserPreferencesForm
              existingPreferences={userPreferences}
              onSave={handleUserPreferencesSave}
              onAccountDeleted={handleLogout}
            />
          )}

          {activeTab === 'players' && (
            <PlayerSearch userHasPreferences={!!userPreferences} />
          )}

          {activeTab === 'changelog' && (
            <Changelog />
          )}
        </main>

        <footer className="App-footer">
          <div className="footer-content">
            <div className="footer-info">
              <p>&copy; 2024 Miniature Tracker. Built for hobbyists, by hobbyists.</p>
              <p>Track your progress, connect with players, and level up your painting game!</p>
            </div>
            <div className="footer-links">
              <button 
                className="footer-link"
                onClick={() => setActiveTab('changelog')}
              >
                What's New
              </button>
              <button 
                className="footer-link"
                onClick={() => setShowFeedbackModal(true)}
              >
                Send Feedback
              </button>
            </div>
          </div>
        </footer>

        {/* Feedback Modal */}
        {showFeedbackModal && (
          <div className="feedback-modal-overlay" onClick={() => setShowFeedbackModal(false)}>
            <div className="feedback-modal-content" onClick={(e) => e.stopPropagation()}>
              <FeedbackForm onClose={() => setShowFeedbackModal(false)} />
            </div>
          </div>
        )}
      </div>
    </ThemeProvider>
  );
}

export default App; 