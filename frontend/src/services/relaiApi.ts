import { supabase } from '@/integrations/supabase/client';

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

// Transform database row to API interface
const transformUser = (row: any): User => ({
  id: row.id,
  name: row.name,
  avatar: row.avatar || '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
  status: row.status
});

const transformTask = (row: any): Task => ({
  id: row.id,
  title: row.title,
  description: row.description || '',
  progress: row.progress,
  relayedFrom: row.relayed_from,
  estimatedHandoff: row.estimated_handoff,
  assignedTo: row.assigned_to,
  status: row.status
});

export const relaiApi = {
  // Users
  async getUsers(): Promise<User[]> {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .order('name');
      
      if (error) throw error;
      return (data || []).map(transformUser);
    } catch (error) {
      console.error('Error fetching users:', error);
      return [];
    }
  },

  async createUser(userData: Omit<User, 'id'>): Promise<User> {
    try {
      const { data, error } = await supabase
        .from('users')
        .insert([{
          name: userData.name,
          avatar: userData.avatar || '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
          status: userData.status
        }])
        .select()
        .single();
      
      if (error) throw error;
      return transformUser(data);
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  },

  // Tasks
  async getTasks(): Promise<Task[]> {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return (data || []).map(transformTask);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return [];
    }
  },

  async createTask(taskData: Omit<Task, 'id'>): Promise<Task> {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .insert([{
          title: taskData.title,
          description: taskData.description,
          progress: taskData.progress,
          relayed_from: taskData.relayedFrom,
          estimated_handoff: taskData.estimatedHandoff,
          assigned_to: taskData.assignedTo,
          status: taskData.status
        }])
        .select()
        .single();
      
      if (error) throw error;
      return transformTask(data);
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },

  async assignTask(taskId: string, userId: string): Promise<Task> {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .update({ assigned_to: userId })
        .eq('id', taskId)
        .select()
        .single();
      
      if (error) throw error;
      return transformTask(data);
    } catch (error) {
      console.error('Error assigning task:', error);
      throw error;
    }
  },

  async updateTaskProgress(taskId: string, progress: number): Promise<Task> {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .update({ progress })
        .eq('id', taskId)
        .select()
        .single();
      
      if (error) throw error;
      return transformTask(data);
    } catch (error) {
      console.error('Error updating task progress:', error);
      throw error;
    }
  },

  async relayTask(taskId: string, fromUser: string, toUser: string): Promise<Task> {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .update({ 
          assigned_to: toUser,
          relayed_from: fromUser
        })
        .eq('id', taskId)
        .select()
        .single();
      
      if (error) throw error;
      return transformTask(data);
    } catch (error) {
      console.error('Error relaying task:', error);
      throw error;
    }
  },

  // Workflows
  async getUserWorkflow(userId: string): Promise<WorkflowData> {
    try {
      // Get active work (tasks assigned to this user with status 'active')
      const { data: activeData, error: activeError } = await supabase
        .from('tasks')
        .select('*')
        .eq('assigned_to', userId)
        .eq('status', 'active')
        .limit(1)
        .single();

      // Get incoming tasks (tasks with status 'pending' assigned to this user)
      const { data: incomingData, error: incomingError } = await supabase
        .from('tasks')
        .select('*')
        .eq('assigned_to', userId)
        .eq('status', 'pending')
        .order('created_at', { ascending: false });

      // Get recent handoffs (completed tasks that were relayed from this user)
      const { data: handoffData, error: handoffError } = await supabase
        .from('tasks')
        .select('*')
        .eq('relayed_from', userId)
        .eq('status', 'completed')
        .order('updated_at', { ascending: false })
        .limit(5);

      return {
        activeWork: activeData && !activeError ? transformTask(activeData) : null,
        incoming: incomingData && !incomingError ? incomingData.map(transformTask) : [],
        recentHandoffs: handoffData && !handoffError ? handoffData.map(transformTask) : []
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