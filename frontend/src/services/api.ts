/**
 * API service for communicating with the miniature tracker backend
 */

import { 
  Miniature, MiniatureCreate, MiniatureUpdate, 
  User, UserCreate, LoginRequest, Token, 
  StatusLogEntryCreate, StatusLogEntryUpdate,
  PasswordResetRequest, PasswordReset,
  Game,
  UserPreferences,
  UserPreferencesCreate,
  UserPreferencesUpdate,
  PlayerSearchRequest,
  PlayerSearchResult,
  CollectionStatistics,
  TrendAnalysis,
  TrendRequest
} from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Will use same domain in production
  : 'http://127.0.0.1:8000'; // Local development

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

// Token management
let authToken: string | null = null;

export const tokenManager = {
  setToken(token: string | null) {
    authToken = token;
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  },

  getToken(): string | null {
    if (!authToken) {
      authToken = localStorage.getItem('authToken');
    }
    return authToken;
  },

  clearToken() {
    authToken = null;
    localStorage.removeItem('authToken');
  }
};

// Initialize token from localStorage
tokenManager.getToken();

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Add auth token if available
  const token = tokenManager.getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If error response isn't JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      
      throw new ApiError(response.status, errorMessage);
    }

    // Handle empty responses (like 204 No Content)
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Network or other errors
    throw new ApiError(0, `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// Authentication API
export const authApi = {
  /**
   * Register a new user
   */
  async register(userData: UserCreate): Promise<{ message: string; user_id: string; email_sent: boolean }> {
    return apiRequest<{ message: string; user_id: string; email_sent: boolean }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Verify email address with token
   */
  async verifyEmail(token: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },

  /**
   * Resend email verification
   */
  async resendVerification(email: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  /**
   * Login user and get token
   */
  async login(credentials: LoginRequest): Promise<Token> {
    return apiRequest<Token>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    return apiRequest<User>('/auth/me');
  },

  /**
   * Logout (client-side token removal)
   */
  logout() {
    tokenManager.clearToken();
  },

  async forgotPassword(request: PasswordResetRequest): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async resetPassword(request: PasswordReset): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
};

export const miniatureApi = {
  /**
   * Get all miniatures for current user
   */
  async getAll(): Promise<Miniature[]> {
    return apiRequest<Miniature[]>('/miniatures');
  },

  /**
   * Get collection statistics for current user
   */
  async getStatistics(): Promise<CollectionStatistics> {
    return apiRequest<CollectionStatistics>('/miniatures/statistics');
  },

  /**
   * Get trend analysis for current user
   */
  async getTrendAnalysis(trendRequest: TrendRequest): Promise<TrendAnalysis> {
    const response = await fetch(`${API_BASE_URL}/miniatures/trends`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tokenManager.getToken()}`
      },
      body: JSON.stringify(trendRequest)
    });

    if (!response.ok) {
      throw new Error('Failed to get trend analysis');
    }

    return response.json();
  },

  /**
   * Get a single miniature by ID
   */
  async getById(id: string): Promise<Miniature> {
    return apiRequest<Miniature>(`/miniatures/${id}`);
  },

  /**
   * Create a new miniature
   */
  async create(miniature: MiniatureCreate): Promise<Miniature> {
    return apiRequest<Miniature>('/miniatures', {
      method: 'POST',
      body: JSON.stringify(miniature),
    });
  },

  /**
   * Update an existing miniature
   */
  async update(id: string, updates: MiniatureUpdate): Promise<Miniature> {
    return apiRequest<Miniature>(`/miniatures/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  /**
   * Delete a miniature
   */
  async delete(id: string): Promise<void> {
    return apiRequest<void>(`/miniatures/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Add a manual status log entry
   */
  async addStatusLog(id: string, logEntry: StatusLogEntryCreate): Promise<Miniature> {
    return apiRequest<Miniature>(`/miniatures/${id}/status-logs`, {
      method: 'POST',
      body: JSON.stringify(logEntry),
    });
  },

  /**
   * Update a status log entry
   */
  async updateStatusLog(id: string, logId: string, updates: StatusLogEntryUpdate): Promise<Miniature> {
    return apiRequest<Miniature>(`/miniatures/${id}/status-logs/${logId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  /**
   * Delete a status log entry
   */
  async deleteStatusLog(id: string, logId: string): Promise<Miniature> {
    return apiRequest<Miniature>(`/miniatures/${id}/status-logs/${logId}`, {
      method: 'DELETE',
    });
  },

  exportCollection: async (format: 'json' | 'csv'): Promise<void> => {
    const response = await fetch(`/miniatures/export/${format}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokenManager.getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to export collection as ${format.toUpperCase()}`);
    }

    // Get filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `miniature_collection.${format}`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Create blob and download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  importCollection: async (
    format: 'json' | 'csv', 
    file: File, 
    replaceExisting: boolean = false
  ): Promise<{
    message: string;
    imported_count: number;
    total_in_file: number;
    replaced_existing: boolean;
  }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`/miniatures/import/${format}?replace_existing=${replaceExisting}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenManager.getToken()}`
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Import failed' }));
      throw new Error(errorData.detail || `Failed to import collection from ${format.toUpperCase()}`);
    }

    return response.json();
  }
};

export const playerApi = {
  /**
   * Get all available games
   */
  async getGames(): Promise<Game[]> {
    return apiRequest<Game[]>('/player/games');
  },

  /**
   * Create a new game (admin function)
   */
  async createGame(name: string, description?: string): Promise<Game> {
    return apiRequest<Game>('/player/games', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  },

  /**
   * Get user preferences
   */
  async getPreferences(): Promise<UserPreferences> {
    return apiRequest<UserPreferences>('/player/preferences');
  },

  /**
   * Create user preferences
   */
  async createPreferences(preferences: UserPreferencesCreate): Promise<UserPreferences> {
    return apiRequest<UserPreferences>('/player/preferences', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  },

  /**
   * Update user preferences
   */
  async updatePreferences(updates: UserPreferencesUpdate): Promise<UserPreferences> {
    return apiRequest<UserPreferences>('/player/preferences', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  /**
   * Search for players
   */
  async searchPlayers(searchRequest: PlayerSearchRequest): Promise<PlayerSearchResult[]> {
    return apiRequest<PlayerSearchResult[]>('/player/search', {
      method: 'POST',
      body: JSON.stringify(searchRequest),
    });
  },
};

export { ApiError }; 