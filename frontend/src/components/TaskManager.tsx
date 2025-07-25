import { useState, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Mic, Bot, ArrowRight, Zap, Settings } from 'lucide-react';
import { relaiApi } from '@/services/relaiApi';
import type { User, Task, WorkflowData } from '@/integrations/mongodb/types';
import CreateUserDialog from './CreateUserDialog';
import CreateTaskDialog from './CreateTaskDialog';
import RelAISidebar from './RelAISidebar';
import RelayChat from './RelayChat';
import { useToast } from '@/hooks/use-toast';

export default function TaskManager() {
  const [message, setMessage] = useState('');
  const [focusedUser, setFocusedUser] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'focused'>('overview');
  const [chatOpen, setChatOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [workflows, setWorkflows] = useState<Record<string, WorkflowData>>({});
  const [users, setUsers] = useState<User[]>([
    {
      _id: 'yazide',
      name: 'Yazide',
      avatar: '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
      status: 'working',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      _id: 'elliott', 
      name: 'Elliott',
      avatar: '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
      status: 'working',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      _id: 'relai',
      name: 'RelAI',
      avatar: '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
      status: 'working',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]);
  
  const [relayWorkflows, setRelayWorkflows] = useState({
    'Yazide': {
      activeWork: {
        _id: '1',
        title: 'Design System Components',
        description: 'Building reusable UI components for the platform',
        progress: 75,
        status: 'active',
        relayedFrom: null,
        estimatedHandoff: '2h',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      incoming: [
        {
          _id: '2',
          title: 'User Research Insights',
          description: 'Analysis findings from recent user interviews',
          progress: 0,
          status: 'waiting',
          relayedFrom: 'RelAI',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      recentHandoffs: [
        {
          _id: '3',
          title: 'Brand Guidelines',
          description: 'Complete visual identity documentation',
          progress: 100,
          status: 'completed',
          relayedFrom: 'Yazide',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]
    },
    'Elliott': {
      activeWork: {
        _id: '4',
        title: 'Payment Gateway Integration',
        description: 'Implementing Stripe payment processing',
        progress: 60,
        status: 'active',
        relayedFrom: 'RelAI',
        estimatedHandoff: '4h',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      incoming: [
        {
          _id: '5',
          title: 'Brand Guidelines Implementation',
          description: 'Apply new visual identity to existing components',
          progress: 0,
          status: 'waiting',
          relayedFrom: 'Yazide',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      recentHandoffs: [
        {
          _id: '6',
          title: 'API Performance Optimization',
          description: 'Database query improvements and caching',
          progress: 100,
          status: 'completed',
          relayedFrom: 'Elliott',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]
    },
    'RelAI': {
      activeWork: {
        _id: '7',
        title: 'Auto Testing & Validation',
        description: 'Running automated test suites and code quality checks',
        progress: 90,
        status: 'active',
        relayedFrom: 'Elliott',
        estimatedHandoff: 'Auto',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      incoming: [
        {
          _id: '8',
          title: 'Code Optimization Queue',
          description: 'Automated performance monitoring and optimization tasks',
          progress: 0,
          status: 'waiting',
          relayedFrom: 'System',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          _id: '11',
          title: 'Security Scan Pipeline',
          description: 'Automated security vulnerability detection and reporting',
          progress: 0,
          status: 'waiting',
          relayedFrom: 'System',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      recentHandoffs: [
        {
          _id: '9',
          title: 'Deploy Ready Package',
          description: 'Automated build validation and deployment preparation',
          progress: 100,
          status: 'completed',
          relayedFrom: 'RelAI',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          _id: '10',
          title: 'Processed Analytics Report',
          description: 'Auto-generated insights from user behavior data',
          progress: 100,
          status: 'completed',
          relayedFrom: 'RelAI',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]
    }
  });
  
  const { toast } = useToast();

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Load users
        const fetchedUsers = await relaiApi.getUsers();
        setUsers(fetchedUsers);
        
        // Load workflows for each user
        const workflowPromises = fetchedUsers.map(async (user) => {
          const workflow = await relaiApi.getUserWorkflow(user._id);
          return [user._id, workflow];
        });
        
        const workflowResults = await Promise.all(workflowPromises);
        const workflowsById = Object.fromEntries(workflowResults);
        setWorkflows(workflowsById);
        
      } catch (error) {
        console.error('Error loading data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load data from database.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [toast]);

  // Simulate progress updates
  useEffect(() => {
    const interval = setInterval(() => {
      Object.keys(relayWorkflows).forEach(user => {
        const workflow = relayWorkflows[user as keyof typeof relayWorkflows];
        if (workflow.activeWork && Math.random() < 0.08) {
          // Update progress in database
          relaiApi.updateTaskProgress(
            workflow.activeWork._id, 
            Math.min(100, workflow.activeWork.progress + Math.floor(Math.random() * 3))
          );
        }
      });
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (type: 'active' | 'waiting' | 'automated' | 'relai') => {
    const variants = {
      active: 'bg-status-active text-white',
      waiting: 'bg-status-waiting text-white',
      automated: 'bg-status-automated text-white',
      relai: 'bg-status-relai text-white'
    };

    const labels = {
      active: 'Active',
      waiting: 'Incoming', 
      automated: 'Automated',
      relai: 'AI Processing'
    };

    return (
      <Badge className={`${variants[type]} border-0 font-medium text-xs`}>
        {labels[type]}
      </Badge>
    );
  };

  const handleSendMessage = () => {
    if (message.trim()) {
      // Simulate message sending / task handoff
      setMessage('');
    }
  };

  const handleUserCreated = async (newUser: User) => {
    try {
      setUsers(prev => [...prev, newUser]);
      // Initialize empty workflow for new user
      setWorkflows(prev => ({
        ...prev,
        [newUser._id]: {
          activeWork: null,
          incoming: [],
          recentHandoffs: []
        }
      }));
      
      toast({
        title: 'Success!',
        description: `${newUser.name} joined the relay system.`,
      });
    } catch (error) {
      console.error('Error in handleUserCreated:', error);
    }
  };

  const handleTaskCreated = async (newTask: Task) => {
    const assignedUser = users.find(u => u._id === newTask.assignedTo);
    if (!assignedUser) return;

    try {
      // Reload workflow for the assigned user
      const updatedWorkflow = await relaiApi.getUserWorkflow(assignedUser._id);
      setWorkflows(prev => ({
        ...prev,
        [assignedUser._id]: updatedWorkflow
      }));

      toast({
        title: 'Task Created!',
        description: `"${newTask.title}" assigned to ${assignedUser.name}.`,
      });
    } catch (error) {
      console.error('Error in handleTaskCreated:', error);
    }
  };

  const handleUserFocus = (userName: string) => {
    if (focusedUser === userName) {
      setFocusedUser(null);
      setViewMode('overview');
    } else {
      setFocusedUser(userName);
      setViewMode('focused');
    }
  };

  const handleTaskAction = async (action: string, taskId: string, data?: any) => {
    // Find the task and its owner
    let taskToUpdate: any = null;
    let taskOwner: string = '';
    
    Object.entries(relayWorkflows).forEach(([userName, workflow]: [string, any]) => {
      if (workflow.activeWork?._id === taskId) {
        taskToUpdate = workflow.activeWork;
        taskOwner = userName;
      } else {
        const incomingTask = workflow.incoming.find((t: any) => t._id === taskId);
        if (incomingTask) {
          taskToUpdate = incomingTask;
          taskOwner = userName;
        }
      }
    });

    if (!taskToUpdate) return;

    try {
      switch (action) {
        case 'complete':
          await relaiApi.updateTaskProgress(taskId, 100);
          // Reload all workflows to reflect changes
          const updatedWorkflows: Record<string, WorkflowData> = {};
          for (const user of users) {
            updatedWorkflows[user._id] = await relaiApi.getUserWorkflow(user._id);
          }
          setWorkflows(updatedWorkflows);
          
          toast({
            title: 'Task Completed',
            description: 'Task has been marked as completed.',
          });
          break;
          
        case 'handoff':
          const targetUserId = data?.targetUser;
          if (targetUserId) {
            await relaiApi.relayTask(taskId, '', targetUserId);
            
            // Reload workflows for affected users
            const reloadedWorkflows: Record<string, WorkflowData> = {};
            for (const user of users) {
              reloadedWorkflows[user._id] = await relaiApi.getUserWorkflow(user._id);
            }
            setWorkflows(reloadedWorkflows);
            
            const targetUser = users.find(u => u._id === targetUserId);
            toast({
              title: 'Task Handed Off',
              description: `Task relayed to ${targetUser?.name}.`,
            });
          }
          break;
          
        case 'delete':
          // For now, just mark as completed since we don't have a delete endpoint
          await relaiApi.updateTaskProgress(taskId, 100);
          
          // Reload all workflows
          const deletedWorkflows: Record<string, WorkflowData> = {};
          for (const user of users) {
            deletedWorkflows[user._id] = await relaiApi.getUserWorkflow(user._id);
          }
          setWorkflows(deletedWorkflows);
          
          toast({
            title: 'Task Removed',
            description: 'Task has been removed from the queue.',
          });
          break;
      }
    } catch (error) {
      console.error('Error in handleTaskAction:', error);
      toast({
        title: 'Error',
        description: 'Failed to perform task action.',
        variant: 'destructive',
      });
    }
  };

  const renderRelayLane = (userName: string, isExpanded: boolean = false) => {
    const workflow = relayWorkflows[userName as keyof typeof relayWorkflows];
    const user = users.find(u => u.name === userName);
    const isRelAI = userName === 'RelAI';
    
    return (
      <div className={`${isExpanded ? 'w-full max-w-5xl' : 'w-full md:min-w-80 md:max-w-80'} transition-all duration-300`}>
        {/* Relay Lane Header */}
        <div className={`backdrop-blur-xl bg-lane-glass rounded-2xl p-6 border border-glass-border shadow-sm mb-6 relative
          ${isRelAI ? 'ring-2 ring-relai-border bg-gradient-to-br from-relai-glow to-transparent' : ''}`}>
          
          {/* Automation Badge for RelAI */}
          {isRelAI && (
            <div className="absolute -top-2 -right-2">
              <div className="bg-gradient-to-r from-status-relai to-status-relai/80 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1 shadow-lg border border-status-relai/30">
                <Bot className="w-3 h-3" />
                <span>Automation</span>
              </div>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className={`w-12 h-12 ring-2 ${isRelAI ? 'ring-status-relai/50 shadow-lg shadow-status-relai/20' : 'ring-border'}`}>
                <AvatarImage src={user?.avatar} alt={userName} />
                <AvatarFallback className={`${isRelAI ? 'bg-status-relai/20 text-status-relai' : 'bg-muted'}`}>
                  {userName === 'RelAI' ? <Bot className="w-6 h-6" /> : userName[0]}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="text-foreground font-semibold text-lg flex items-center space-x-2">
                  <span>{isRelAI ? 'RelAI Automation' : userName}</span>
                  {isRelAI && <Bot className="w-4 h-4 text-status-relai" />}
                </h3>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 ${isRelAI ? 'bg-status-relai' : 'bg-status-active'} rounded-full ${isRelAI ? 'animate-pulse shadow-sm shadow-status-relai' : 'animate-pulse'}`} />
                  <span className="text-muted-foreground text-sm">
                    {isRelAI ? 'Auto Processing' : 'In Relay'}
                  </span>
                </div>
              </div>
            </div>
            {workflow.activeWork && (
              <div className="text-right">
                <div className="text-muted-foreground text-xs">{isRelAI ? 'Next Process' : 'Est. Handoff'}</div>
                <div className="text-foreground font-medium text-sm">{workflow.activeWork.estimatedHandoff}</div>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          {/* Active Work - The Track */}
          {workflow.activeWork && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-muted-foreground font-semibold text-sm uppercase tracking-wide flex items-center space-x-2">
                  <div className={`w-3 h-3 ${isRelAI ? 'bg-status-relai' : 'bg-status-active'} rounded-full`} />
                  <span>{isRelAI ? 'Auto Processing' : 'Active Lane'}</span>
                </h4>
                {getStatusBadge(isRelAI ? 'relai' : 'active')}
              </div>
              <Card className={`backdrop-blur-xl bg-glass-bg rounded-xl p-5 border border-glass-border shadow-sm hover:shadow-md transition-all duration-200 relative
                ${isRelAI ? 'ring-1 ring-status-relai/20 bg-gradient-to-br from-relai-glow to-transparent' : ''}`}>
                
                {/* Flow Arrow from Previous */}
                {workflow.activeWork.relayedFrom && (
                  <div className="absolute -left-8 top-1/2 transform -translate-y-1/2 flex items-center space-x-2 text-status-active">
                    <ArrowRight className="w-5 h-5 animate-pulse" />
                  </div>
                )}
                
                <div className="space-y-4">
                  <div>
                    <h5 className="text-foreground font-semibold text-base leading-tight mb-2">
                      {workflow.activeWork.title}
                    </h5>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      {workflow.activeWork.description}
                    </p>
                  </div>
                  
                  {workflow.activeWork.relayedFrom && (
                    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs 
                      ${isRelAI ? 'bg-status-relai/10 text-status-relai border border-status-relai/20' : 'bg-status-active/10 text-status-active border border-status-active/20'}`}>
                      <ArrowRight className="w-3 h-3" />
                      <span>Relayed from {workflow.activeWork.relayedFrom}</span>
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Progress</span>
                      <span>{workflow.activeWork.progress}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2 relative overflow-hidden">
                      <div 
                        className={`${isRelAI ? 'bg-status-relai' : 'bg-status-active'} rounded-full h-2 transition-all duration-500 relative`}
                        style={{ width: `${workflow.activeWork.progress}%` }}
                      >
                        {/* Progress pulse for active work */}
                        <div className={`absolute inset-0 ${isRelAI ? 'bg-status-relai' : 'bg-status-active'} rounded-full animate-pulse opacity-50`} />
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Incoming Queue */}
          {workflow.incoming.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-muted-foreground font-medium text-sm uppercase tracking-wide flex items-center space-x-2">
                  <div className={`w-3 h-3 ${isRelAI ? 'bg-status-automated' : 'bg-status-waiting'} rounded-full animate-pulse`} />
                  <span>{isRelAI ? 'Auto Queue' : 'Incoming Queue'}</span>
                </h4>
                <div className="text-xs text-muted-foreground">{workflow.incoming.length} waiting</div>
              </div>
              {workflow.incoming.map((item, index) => (
                <Card key={item._id} className="backdrop-blur-xl bg-glass-frosted rounded-xl p-4 border border-glass-border hover:bg-glass-bg transition-all duration-200 relative">
                  
                  {/* Queue position indicator */}
                  <div className="absolute -left-3 top-4 w-6 h-6 bg-status-waiting text-white rounded-full flex items-center justify-center text-xs font-medium">
                    {index + 1}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <h5 className="text-foreground font-medium text-sm leading-tight">
                        {item.title}
                      </h5>
                      <span className="text-xs text-muted-foreground">15 min ago</span>
                    </div>
                    <p className="text-muted-foreground text-xs leading-relaxed">
                      {item.description}
                    </p>
                    <div className="inline-flex items-center space-x-1 px-2 py-1 bg-status-waiting/10 text-status-waiting rounded-md text-xs border border-status-waiting/20">
                      <ArrowRight className="w-3 h-3" />
                      <span>From {item.relayedFrom}</span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Recent Handoffs */}
          {workflow.recentHandoffs.length > 0 && !isExpanded && (
            <div className="space-y-3">
              <h4 className="text-muted-foreground font-medium text-xs uppercase tracking-wide flex items-center space-x-2">
                <div className="w-2 h-2 bg-muted-foreground/50 rounded-full" />
                <span>Recent Handoffs</span>
              </h4>
              {workflow.recentHandoffs.slice(0, 2).map((item) => (
                <Card key={item._id} className="backdrop-blur-xl bg-glass-frosted rounded-xl p-3 border border-glass-border opacity-60 relative">
                  
                  {/* Handoff arrow */}
                  <div className="absolute -right-8 top-1/2 transform -translate-y-1/2 text-muted-foreground">
                    <ArrowRight className="w-4 h-4" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <h5 className="text-foreground font-medium text-xs">
                      {item.title}
                    </h5>
                    <div className="text-right">
                      <div className="text-xs text-muted-foreground flex items-center space-x-1">
                        <ArrowRight className="w-3 h-3" />
                        <span>Elliott</span>
                      </div>
                      <div className="text-xs text-muted-foreground">1h ago</div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-enterprise flex">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-3 md:p-6 pb-2 md:pb-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 animate-slide-up">
            <div>
              <h1 className="text-xl md:text-2xl font-semibold text-foreground mb-1">
                {viewMode === 'focused' && focusedUser ? `${focusedUser} Relay Lane` : 'Relay Command Center'}
              </h1>
              <p className="text-muted-foreground text-xs md:text-sm">
                {viewMode === 'focused' ? 'Individual lane focus' : 'Live handoff monitoring'}
              </p>
            </div>
            
            {viewMode === 'overview' && (
              <div className="flex items-center space-x-2 md:space-x-4 text-xs md:text-sm text-muted-foreground">
                <div>Active: {Object.values(relayWorkflows).filter(w => w.activeWork).length}</div>
                <div>•</div>
                <div>In Queue: {Object.values(relayWorkflows).reduce((acc, w) => acc + w.incoming.length, 0)}</div>
              </div>
            )}
          </div>
        </div>

        {/* Relay Lanes */}
        <div className="flex-1 overflow-hidden px-3 md:px-6 pb-20 md:pb-24">
          <div className="h-full overflow-x-auto">
            <div className={`flex ${viewMode === 'focused' ? 'justify-center' : 'flex-col md:flex-row md:space-x-6 space-y-4 md:space-y-0'} h-full ${viewMode === 'overview' ? 'md:min-w-max' : ''}`}>
              {viewMode === 'focused' && focusedUser ? (
                renderRelayLane(focusedUser, true)
              ) : (
                users.map(user => renderRelayLane(user.name, false))
              )}
            </div>
          </div>
        </div>

        {/* Enhanced Command Center Toolbar */}
        <div className="fixed bottom-3 md:bottom-6 left-1/2 transform -translate-x-1/2 z-50 w-[95vw] md:w-auto">
          <div className="backdrop-blur-xl bg-glass-bg rounded-xl md:rounded-2xl px-3 md:px-6 py-2 md:py-3 border border-glass-border shadow-lg overflow-x-auto">
            <div className="flex items-center space-x-1 md:space-x-1 min-w-max">
              {/* Profile Switcher with Active State */}
              {users.map((user) => (
                <Button
                  key={user._id}
                  variant="ghost"
                  size="sm"
                  onClick={() => handleUserFocus(user.name)}
                  className={`
                    ${focusedUser === user.name 
                      ? 'bg-glass-frosted ring-2 ring-border scale-105 md:scale-110 h-8 md:h-10 px-2 md:px-4' 
                      : 'hover:bg-glass-frosted h-7 md:h-8 px-2 md:px-3'
                    } 
                    text-foreground flex items-center space-x-1 md:space-x-2 rounded-lg md:rounded-xl transition-all duration-200
                    ${user.name === 'RelAI' ? 'border border-status-relai/30' : ''}
                  `}
                >
                  <Avatar className={`${focusedUser === user.name ? 'w-5 h-5 md:w-6 md:h-6' : 'w-4 h-4 md:w-5 md:h-5'} ${user.name === 'RelAI' ? 'ring-1 ring-status-relai/50' : ''}`}>
                    <AvatarImage src={user.avatar} alt={user.name} />
                    <AvatarFallback className={`text-xs ${user.name === 'RelAI' ? 'bg-status-relai/20 text-status-relai' : 'bg-muted'}`}>
                      {user.name === 'RelAI' ? <Bot className="w-2 h-2 md:w-3 md:h-3" /> : user.name[0]}
                    </AvatarFallback>
                  </Avatar>
                  <span className={`${focusedUser === user.name ? 'text-xs md:text-sm font-semibold' : 'text-xs font-medium'} hidden sm:inline`}>
                    {user.name}
                  </span>
                  {relayWorkflows[user.name as keyof typeof relayWorkflows]?.activeWork && (
                    <div className={`w-1 h-1 md:w-1.5 md:h-1.5 ${user.name === 'RelAI' ? 'bg-status-relai' : 'bg-status-active'} rounded-full animate-pulse`} />
                  )}
                  {user.name === 'RelAI' && focusedUser !== user.name && (
                    <Zap className="w-2 h-2 md:w-3 md:h-3 text-status-relai" />
                  )}
                </Button>
              ))}
              
              <div className="w-px h-4 md:h-6 bg-border mx-2 md:mx-3" />
              
              {/* View Mode Toggle */}
              <div className="flex items-center space-x-1 bg-muted rounded-lg p-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFocusedUser(null);
                    setViewMode('overview');
                  }}
                  className={`
                    ${viewMode === 'overview' 
                      ? 'bg-background shadow-sm text-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                    } 
                    h-6 md:h-7 px-2 md:px-3 rounded-md text-xs font-medium transition-all
                  `}
                >
                  <span className="hidden sm:inline">All Lanes</span>
                  <span className="sm:hidden">All</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`
                    ${viewMode === 'focused' && focusedUser
                      ? 'bg-background shadow-sm text-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                    } 
                    h-6 md:h-7 px-2 md:px-3 rounded-md text-xs font-medium transition-all
                  `}
                >
                  Focus
                </Button>
              </div>
              
              <div className="w-px h-4 md:h-6 bg-border mx-2 md:mx-3" />
              
              {/* Action Buttons */}
              <div className="flex items-center space-x-1">
                <CreateUserDialog onUserCreated={handleUserCreated} />
                <CreateTaskDialog users={users} onTaskCreated={handleTaskCreated} />
              </div>
              
              <div className="w-px h-4 md:h-6 bg-border mx-2 md:mx-3" />
              
              {/* Quick Actions */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setChatOpen(true)}
                className="text-foreground hover:bg-glass-frosted h-7 md:h-8 px-2 md:px-3 rounded-lg md:rounded-xl flex items-center space-x-1 md:space-x-2"
              >
                <Bot className="w-3 h-3" />
                <span className="text-xs hidden sm:inline">Relay Chat</span>
              </Button>
            </div>
          </div>
        </div>
        
        {/* Relay Chat Dialog */}
        <RelayChat
          open={chatOpen}
          onOpenChange={setChatOpen}
          users={users}
          workflows={relayWorkflows}
          onTaskAction={handleTaskAction}
        />
      </div>

      {/* RelAI Sidebar */}
      <RelAISidebar
        users={users}
        workflows={relayWorkflows}
        focusedUser={focusedUser}
        onTaskAction={handleTaskAction}
      />
    </div>
  );
}