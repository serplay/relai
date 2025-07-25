// MongoDB types for frontend integration
// These types match the backend MongoDB schema

export interface User {
  _id: string;
  name: string;
  avatar?: string;
  status: 'working' | 'idle';
  created_at: string;
  updated_at: string;
}

export interface Task {
  _id: string;
  title: string;
  description: string;
  progress: number;
  status: 'active' | 'waiting' | 'completed';
  assignedTo?: string;
  relayedFrom?: string;
  estimatedHandoff?: string;
  relayedAt?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkflowData {
  activeWork: Task | null;
  incoming: Task[];
  recentHandoffs: Task[];
}

export interface CreateUserRequest {
  name: string;
  avatar?: string;
  status: 'working' | 'idle';
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  progress?: number;
  status?: 'active' | 'waiting' | 'completed';
  assignedTo?: string;
  relayedFrom?: string;
  estimatedHandoff?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  progress?: number;
  status?: 'active' | 'waiting' | 'completed';
  assignedTo?: string;
  relayedFrom?: string;
  estimatedHandoff?: string;
}

export interface TaskAssignRequest {
  assignedTo: string;
}

export interface TaskProgressRequest {
  progress: number;
}

export interface TaskRelayRequest {
  from_user: string;
  to_user: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
} 