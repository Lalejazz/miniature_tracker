/**
 * API service for communicating with the miniature tracker backend
 */

import { Miniature, MiniatureCreate, MiniatureUpdate, User, UserCreate, LoginRequest, Token } from '../types';

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
    if (authToken) return authToken;
    authToken = localStorage.getItem('authToken');
    return authToken;
  },

  clearToken() {
    authToken = null;
    localStorage.removeItem('authToken');
  }
};

async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = tokenManager.getToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };

  // Add authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    headers,
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    
    // If unauthorized, clear token
    if (response.status === 401) {
      tokenManager.clearToken();
    }
    
    throw new ApiError(response.status, errorText);
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const authApi = {
  /**
   * Register a new user
   */
  async register(userData: UserCreate): Promise<User> {
    return apiRequest<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
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
  }
};

export { ApiError }; 