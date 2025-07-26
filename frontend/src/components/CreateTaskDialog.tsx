import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Zap } from 'lucide-react';
import { relaiApi, Task, User } from '@/services/relaiApi';
import { useToast } from '@/hooks/use-toast';

interface CreateTaskDialogProps {
  users: User[];
  onTaskCreated: (task: Task) => void;
}

export default function CreateTaskDialog({ users, onTaskCreated }: CreateTaskDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    naturalLanguage: '',
    assignedTo: '',
  });
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.naturalLanguage.trim() || !formData.assignedTo) return;

    setLoading(true);
    try {
      const taskData = {
        title: formData.naturalLanguage.slice(0, 50) + (formData.naturalLanguage.length > 50 ? '...' : ''),
        description: formData.naturalLanguage,
        progress: 0,
        relayedFrom: null,
        estimatedHandoff: '2h',
        assignedTo: formData.assignedTo,
        status: 'active' as const,
      };
      
      const newTask = await relaiApi.createTask(taskData);
      onTaskCreated(newTask);
      
      toast({
        title: 'Task Created',
        description: `Task assigned to ${users.find(u => u.id === formData.assignedTo)?.name}.`,
      });
      
      setFormData({ 
        naturalLanguage: '', 
        assignedTo: '', 
      });
      setOpen(false);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create task. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 px-3 rounded-xl flex items-center space-x-2 bg-primary/10 hover:bg-primary/20 border-primary/20"
        >
          <Plus className="w-3 h-3" />
          <span className="text-xs">Create Task</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg" aria-describedby="task-dialog-description">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5" />
            <span>Create New Task</span>
          </DialogTitle>
        </DialogHeader>
        <div id="task-dialog-description" className="sr-only">
          Dialog for creating a new task with natural language description and user assignment
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="naturalLanguage">What needs to be done?</Label>
            <Textarea
              id="naturalLanguage"
              value={formData.naturalLanguage}
              onChange={(e) => setFormData(prev => ({ ...prev, naturalLanguage: e.target.value }))}
              placeholder="Describe what needs to be done in natural language..."
              rows={4}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="assignedTo">Who are you?</Label>
            <Select 
              value={formData.assignedTo} 
              onValueChange={(value) => setFormData(prev => ({ ...prev, assignedTo: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select yourself" />
              </SelectTrigger>
              <SelectContent>
                {users.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex justify-end space-x-2 pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => setOpen(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !formData.naturalLanguage.trim() || !formData.assignedTo}>
              {loading ? 'Creating...' : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}