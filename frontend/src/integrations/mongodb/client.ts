// MongoDB client for frontend integration
// This replaces the Supabase client with MongoDB API calls

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface MongoDBConfig {
  apiBaseUrl: string;
}

export const mongodbConfig: MongoDBConfig = {
  apiBaseUrl: API_BASE_URL,
};

// Helper function for API calls
async function apiCall<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${mongodbConfig.apiBaseUrl}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Export the API client
export const mongodbClient = {
  apiCall,
  config: mongodbConfig,
}; 