import { mongodbClient } from '@/integrations/mongodb/client';
import type { 
  User, 
  Task, 
  WorkflowData, 
  CreateUserRequest, 
  CreateTaskRequest, 
  UpdateTaskRequest,
  TaskAssignRequest,
  TaskProgressRequest,
  TaskRelayRequest
} from '@/integrations/mongodb/types';

// Transform database row to API interface
const transformUser = (row: any): User => ({
  _id: row._id,
  name: row.name,
  avatar: row.avatar || '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
  status: row.status,
  created_at: row.created_at,
  updated_at: row.updated_at
});

const transformTask = (row: any): Task => ({
  _id: row._id,
  title: row.title,
  description: row.description || '',
  progress: row.progress,
  relayedFrom: row.relayedFrom,
  estimatedHandoff: row.estimatedHandoff,
  assignedTo: row.assignedTo,
  status: row.status,
  relayedAt: row.relayedAt,
  created_at: row.created_at,
  updated_at: row.updated_at
});

export const mongodbApi = {
  // Users
  async getUsers(): Promise<User[]> {
    try {
      const data = await mongodbClient.apiCall<User[]>('/users');
      return data.map(transformUser);
    } catch (error) {
      console.error('Error fetching users:', error);
      return [];
    }
  },

  async createUser(userData: CreateUserRequest): Promise<User> {
    try {
      const data = await mongodbClient.apiCall<User>('/users', {
        method: 'POST',
        body: JSON.stringify(userData)
      });
      return transformUser(data);
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  },

  // Tasks
  async getTasks(): Promise<Task[]> {
    try {
      const data = await mongodbClient.apiCall<Task[]>('/tasks');
      return data.map(transformTask);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return [];
    }
  },

  async createTask(taskData: CreateTaskRequest): Promise<Task> {
    try {
      const data = await mongodbClient.apiCall<Task>('/tasks', {
        method: 'POST',
        body: JSON.stringify(taskData)
      });
      return transformTask(data);
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },

  async assignTask(taskId: string, userId: string): Promise<Task> {
    try {
      const assignData: TaskAssignRequest = { assignedTo: userId };
      const data = await mongodbClient.apiCall<Task>(`/tasks/${taskId}/assign`, {
        method: 'PUT',
        body: JSON.stringify(assignData)
      });
      return transformTask(data);
    } catch (error) {
      console.error('Error assigning task:', error);
      throw error;
    }
  },

  async updateTaskProgress(taskId: string, progress: number): Promise<Task> {
    try {
      const progressData: TaskProgressRequest = { progress };
      const data = await mongodbClient.apiCall<Task>(`/tasks/${taskId}/progress`, {
        method: 'PUT',
        body: JSON.stringify(progressData)
      });
      return transformTask(data);
    } catch (error) {
      console.error('Error updating task progress:', error);
      throw error;
    }
  },

  async relayTask(taskId: string, fromUser: string, toUser: string): Promise<Task> {
    try {
      const relayData: TaskRelayRequest = { from_user: fromUser, to_user: toUser };
      const data = await mongodbClient.apiCall<Task>(`/tasks/${taskId}/relay`, {
        method: 'POST',
        body: JSON.stringify(relayData)
      });
      return transformTask(data);
    } catch (error) {
      console.error('Error relaying task:', error);
      throw error;
    }
  },

  // Workflows
  async getUserWorkflow(userId: string): Promise<WorkflowData> {
    try {
      const data = await mongodbClient.apiCall<WorkflowData>(`/workflows/${userId}`);
      return {
        activeWork: data.activeWork ? transformTask(data.activeWork) : null,
        incoming: data.incoming.map(transformTask),
        recentHandoffs: data.recentHandoffs.map(transformTask)
      };
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