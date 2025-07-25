import { useState, useRef, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Bot, Send, Check, X, Edit, ArrowRight, Trash2, Clock, User, Zap } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { User as UserType, Task } from '@/services/relaiApi';

interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  actions?: TaskAction[];
  taskRef?: string;
}

interface TaskAction {
  type: 'handoff' | 'complete' | 'edit' | 'delete' | 'accept' | 'assign';
  label: string;
  taskId: string;
  targetUser?: string;
  variant?: 'default' | 'destructive' | 'secondary';
}

interface RelayChatProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  users: UserType[];
  currentUser?: UserType;
  workflows: any;
  onTaskAction: (action: string, taskId: string, data?: any) => void;
}

export default function RelayChat({ 
  open, 
  onOpenChange, 
  users, 
  currentUser, 
  workflows, 
  onTaskAction 
}: RelayChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      content: "👋 Hey! I'm RelAI, your workflow assistant. I can help you manage tasks, handle handoffs, and keep your relay flowing smoothly. What can I help you with?",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getAvailableActions = (taskId: string, currentOwner: string): TaskAction[] => {
    const otherUsers = users.filter(u => u.name !== currentOwner && u.name !== 'RelAI');
    const actions: TaskAction[] = [];

    // Complete task
    actions.push({
      type: 'complete',
      label: '✅ Mark Complete',
      taskId,
      variant: 'default'
    });

    // Edit task
    actions.push({
      type: 'edit',
      label: '✏️ Edit Task',
      taskId,
      variant: 'secondary'
    });

    // Handoff to other users
    otherUsers.forEach(user => {
      actions.push({
        type: 'handoff',
        label: `➡️ Handoff to ${user.name}`,
        taskId,
        targetUser: user.name,
        variant: 'secondary'
      });
    });

    // Delete task
    actions.push({
      type: 'delete',
      label: '🗑️ Delete',
      taskId,
      variant: 'destructive'
    });

    return actions;
  };

  const simulateAIResponse = async (userMessage: string): Promise<ChatMessage> => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Get all active tasks across users
    const allTasks: { task: any, owner: string }[] = [];
    Object.entries(workflows).forEach(([userName, workflow]: [string, any]) => {
      if (workflow.activeWork) {
        allTasks.push({ task: workflow.activeWork, owner: userName });
      }
      workflow.incoming.forEach((task: any) => {
        allTasks.push({ task, owner: userName });
      });
    });

    let content = '';
    let actions: TaskAction[] = [];

    if (lowerMessage.includes('status') || lowerMessage.includes('overview')) {
      const activeCount = Object.values(workflows).filter((w: any) => w.activeWork).length;
      const queueCount = Object.values(workflows).reduce((acc: number, w: any) => acc + w.incoming.length, 0);
      
      content = `📊 **Relay Status Update**\n\n• ${activeCount} active tasks in progress\n• ${queueCount} tasks in queue\n• ${users.length} team members online\n\nEverything's flowing smoothly! Need help with any specific task?`;
    }
    else if (lowerMessage.includes('handoff') || lowerMessage.includes('relay')) {
      content = "🔄 **Quick Handoff Options**\n\nI can help you relay tasks between team members. Which task would you like to handoff?";
      
      // Add handoff actions for active tasks
      allTasks.forEach(({ task, owner }) => {
        if (task.progress < 100) {
          const targetUsers = users.filter(u => u.name !== owner && u.name !== 'RelAI');
          targetUsers.forEach(user => {
            actions.push({
              type: 'handoff',
              label: `${task.title} → ${user.name}`,
              taskId: task.id,
              targetUser: user.name,
              variant: 'secondary'
            });
          });
        }
      });
    }
    else if (lowerMessage.includes('complete') || lowerMessage.includes('done') || lowerMessage.includes('finish')) {
      content = "✅ **Complete Tasks**\n\nWhich tasks are ready to be marked as complete?";
      
      allTasks.forEach(({ task, owner }) => {
        if (task.progress >= 75) {
          actions.push({
            type: 'complete',
            label: `Complete: ${task.title}`,
            taskId: task.id,
            variant: 'default'
          });
        }
      });
    }
    else if (lowerMessage.includes('help') || lowerMessage.includes('what can')) {
      content = `🤖 **I can help you with:**\n\n• **Task Management** - Complete, edit, or delete tasks\n• **Smart Handoffs** - Route tasks to the right team member\n• **Status Updates** - Get overview of all active work\n• **Queue Management** - Prioritize and organize incoming tasks\n• **Automation** - Set up workflow rules and triggers\n\nJust tell me what you need! For example:\n- "Handoff task X to Yazide"\n- "Mark design system as complete"\n- "Show me status overview"`;
    }
    else if (lowerMessage.includes('assign') || lowerMessage.includes('create')) {
      content = "📝 **Task Assignment**\n\nI can help assign new tasks or reassign existing ones. Use the 'Create Task' button in the toolbar for new tasks, or tell me which existing task to reassign!";
    }
    else {
      // Smart response based on task analysis
      const highProgressTasks = allTasks.filter(({ task }) => task.progress >= 80);
      const stuckTasks = allTasks.filter(({ task }) => task.progress < 30);
      
      if (highProgressTasks.length > 0) {
        content = `🎯 I noticed you have ${highProgressTasks.length} task(s) almost ready to complete:\n\n${highProgressTasks.map(({ task, owner }) => `• **${task.title}** (${owner} - ${task.progress}%)`).join('\n')}\n\nWant me to help wrap these up?`;
        
        highProgressTasks.forEach(({ task }) => {
          actions.push({
            type: 'complete',
            label: `Complete: ${task.title}`,
            taskId: task.id,
            variant: 'default'
          });
        });
      } else if (stuckTasks.length > 0) {
        content = `🔍 I see ${stuckTasks.length} task(s) that might need attention:\n\n${stuckTasks.map(({ task, owner }) => `• **${task.title}** (${owner} - ${task.progress}%)`).join('\n')}\n\nNeed help moving these forward?`;
      } else {
        content = "💡 **RelAI at your service!**\n\nI'm here to help optimize your workflow. You can ask me to:\n\n• Complete or handoff tasks\n• Check team status\n• Manage your task queue\n• Automate routine handoffs\n\nWhat would you like to do?";
      }
    }

    return {
      id: Date.now().toString(),
      type: 'bot',
      content,
      timestamp: new Date(),
      actions: actions.slice(0, 6) // Limit to 6 actions for UI
    };
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI thinking time
    setTimeout(async () => {
      const aiResponse = await simulateAIResponse(input);
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  const handleAction = (action: TaskAction) => {
    const task = Object.values(workflows)
      .flatMap((w: any) => [w.activeWork, ...w.incoming, ...w.recentHandoffs])
      .find((t: any) => t?.id === action.taskId);

    let message = '';
    
    switch (action.type) {
      case 'complete':
        onTaskAction('complete', action.taskId);
        message = `✅ Marked "${task?.title}" as complete!`;
        break;
      case 'handoff':
        onTaskAction('handoff', action.taskId, { targetUser: action.targetUser });
        message = `🔄 Handed off "${task?.title}" to ${action.targetUser}`;
        break;
      case 'edit':
        onTaskAction('edit', action.taskId);
        message = `✏️ Editing "${task?.title}"`;
        break;
      case 'delete':
        onTaskAction('delete', action.taskId);
        message = `🗑️ Deleted "${task?.title}"`;
        break;
    }

    toast({
      title: 'Action Completed',
      description: message,
    });

    // Add confirmation message to chat
    const confirmMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'bot',
      content: `${message}\n\nIs there anything else I can help you with?`,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, confirmMessage]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl h-[80vh] flex flex-col">
        <DialogHeader className="pb-4">
          <DialogTitle className="flex items-center space-x-2">
            <div className="relative">
              <Bot className="w-6 h-6 text-primary" />
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-background"></div>
            </div>
            <span>RelAI Assistant</span>
            <Badge variant="secondary" className="text-xs">AI Powered</Badge>
          </DialogTitle>
        </DialogHeader>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                <div className="flex items-start space-x-2">
                  {message.type === 'bot' && (
                    <Avatar className="w-8 h-8 ring-2 ring-primary/20">
                      <AvatarFallback className="bg-primary/10 text-primary">
                        <Bot className="w-4 h-4" />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  
                  <div className="flex-1">
                    <Card className={`p-3 ${
                      message.type === 'user' 
                        ? 'bg-primary text-primary-foreground ml-8' 
                        : 'bg-muted'
                    }`}>
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </div>
                    </Card>
                    
                    {/* Action Buttons */}
                    {message.actions && message.actions.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {message.actions.map((action, index) => (
                          <Button
                            key={index}
                            variant={action.variant || 'outline'}
                            size="sm"
                            onClick={() => handleAction(action)}
                            className="text-xs h-7"
                          >
                            {action.label}
                          </Button>
                        ))}
                      </div>
                    )}
                    
                    <div className="text-xs text-muted-foreground mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-2">
                <Avatar className="w-8 h-8 ring-2 ring-primary/20">
                  <AvatarFallback className="bg-primary/10 text-primary">
                    <Bot className="w-4 h-4" />
                  </AvatarFallback>
                </Avatar>
                <Card className="bg-muted p-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </Card>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t pt-4">
          <div className="flex space-x-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask RelAI to help with tasks, handoffs, or workflow..."
              className="flex-1"
            />
            <Button onClick={handleSend} disabled={!input.trim() || isTyping}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 mt-3">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setInput('Show me status overview')}
              className="text-xs"
            >
              📊 Status
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setInput('Help me with handoffs')}
              className="text-xs"
            >
              🔄 Handoffs
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setInput('What tasks can be completed?')}
              className="text-xs"
            >
              ✅ Complete
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setInput('Help')}
              className="text-xs"
            >
              ❓ Help
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}