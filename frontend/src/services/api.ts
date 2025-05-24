/**
 * API service for communicating with the miniature tracker backend
 */

import { Miniature, MiniatureCreate, MiniatureUpdate } from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Will use same domain in production
  : 'http://127.0.0.1:8000'; // Local development

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText);
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const miniatureApi = {
  /**
   * Get all miniatures
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