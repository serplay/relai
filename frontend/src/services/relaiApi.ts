const API_BASE = 'https://relai.es/api';

export interface User {
  id: string;
  name: string;
  avatar: string;
  status: 'working' | 'idle';
}

export interface Task {
  id: string;
  title: string;
  description: string;
  progress: number;
  relayedFrom: string | null;
  estimatedHandoff: string;
  assignedTo?: string;
  status: 'active' | 'waiting' | 'completed';
  timeReceived?: string;
  timeHandedOff?: string;
  relayedTo?: string;
}

export interface WorkflowData {
  activeWork: Task | null;
  incoming: Task[];
  recentHandoffs: Task[];
}

// User API functions
export const relaiApi = {
  // Users
  async getUsers(): Promise<User[]> {
    try {
      const response = await fetch(`${API_BASE}/users`);
      if (!response.ok) throw new Error('Failed to fetch users');
      return await response.json();
    } catch (error) {
      console.error('Error fetching users:', error);
      // Fallback to mock data for presentation
      return [];
    }
  },

  async createUser(userData: Omit<User, 'id'>): Promise<User> {
    try {
      const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      if (!response.ok) throw new Error('Failed to create user');
      return await response.json();
    } catch (error) {
      console.error('Error creating user:', error);
      // Return mock response for presentation
      return {
        id: Date.now().toString(),
        ...userData,
      };
    }
  },

  // Tasks
  async getTasks(): Promise<Task[]> {
    try {
      const response = await fetch(`${API_BASE}/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      return await response.json();
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return [];
    }
  },

  async createTask(taskData: Omit<Task, 'id'>): Promise<Task> {
    try {
      const response = await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      if (!response.ok) throw new Error('Failed to create task');
      return await response.json();
    } catch (error) {
      console.error('Error creating task:', error);
      // Return mock response for presentation
      return {
        id: Date.now().toString(),
        ...taskData,
      };
    }
  },

  async assignTask(taskId: string, userId: string): Promise<Task> {
    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}/assign`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assignedTo: userId }),
      });
      if (!response.ok) throw new Error('Failed to assign task');
      return await response.json();
    } catch (error) {
      console.error('Error assigning task:', error);
      throw error;
    }
  },

  async updateTaskProgress(taskId: string, progress: number): Promise<Task> {
    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}/progress`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ progress }),
      });
      if (!response.ok) throw new Error('Failed to update task progress');
      return await response.json();
    } catch (error) {
      console.error('Error updating task progress:', error);
      throw error;
    }
  },

  async relayTask(taskId: string, fromUser: string, toUser: string): Promise<Task> {
    try {
      const response = await fetch(`${API_BASE}/tasks/${taskId}/relay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from: fromUser, to: toUser }),
      });
      if (!response.ok) throw new Error('Failed to relay task');
      return await response.json();
    } catch (error) {
      console.error('Error relaying task:', error);
      throw error;
    }
  },

  // Workflows
  async getUserWorkflow(userId: string): Promise<WorkflowData> {
    try {
      const response = await fetch(`${API_BASE}/users/${userId}/workflow`);
      if (!response.ok) throw new Error('Failed to fetch user workflow');
      return await response.json();
    } catch (error) {
      console.error('Error fetching user workflow:', error);
      return {
        activeWork: null,
        incoming: [],
        recentHandoffs: [],
      };
    }
  },
};