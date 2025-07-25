import { useState, useEffect } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send, Mic, Bot, ArrowRight, Zap } from 'lucide-react';

interface User {
  id: string; // username = id for simplicity
  name: string;
  avatar: string;
  status: 'working' | 'idle';
}

const users: User[] = [
  {
    id: 'yazide',
    name: 'Yazide',
    avatar: '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
    status: 'working'
  },
  {
    id: 'elliott', 
    name: 'Elliott',
    avatar: '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
    status: 'working'
  },
  {
    id: 'relai',
    name: 'RelAI',
    avatar: '/lovable-uploads/ad7ac94b-537e-4407-8cdc-26c4a1f25f84.png',
    status: 'working'
  }
];

const relayWorkflows = {
  'Yazide': {
    activeWork: {
      id: '1',
      title: 'Design System Components',
      description: 'Building reusable UI components for the platform',
      progress: 75,
      relayedFrom: null,
      estimatedHandoff: '2h'
    },
    incoming: [
      {
        id: '2',
        title: 'User Research Insights',
        description: 'Analysis findings from recent user interviews',
        relayedFrom: 'RelAI',
        timeReceived: '15 min ago'
      }
    ],
    recentHandoffs: [
      {
        id: '3',
        title: 'Brand Guidelines',
        description: 'Complete visual identity documentation',
        relayedTo: 'Elliott',
        timeHandedOff: '1h ago'
      }
    ]
  },
  'Elliott': {
    activeWork: {
      id: '4',
      title: 'Payment Gateway Integration',
      description: 'Implementing Stripe payment processing',
      progress: 60,
      relayedFrom: 'RelAI',
      estimatedHandoff: '4h'
    },
    incoming: [
      {
        id: '5',
        title: 'Brand Guidelines Implementation',
        description: 'Apply new visual identity to existing components',
        relayedFrom: 'Yazide',
        timeReceived: '45 min ago'
      }
    ],
    recentHandoffs: [
      {
        id: '6',
        title: 'API Performance Optimization',
        description: 'Database query improvements and caching',
        relayedTo: 'RelAI',
        timeHandedOff: '3h ago'
      }
    ]
  },
  'RelAI': {
    activeWork: {
      id: '7',
      title: 'Auto Testing & Validation',
      description: 'Running automated test suites and code quality checks',
      progress: 90,
      relayedFrom: 'Elliott',
      estimatedHandoff: 'Auto'
    },
    incoming: [
      {
        id: '8',
        title: 'Code Optimization Queue',
        description: 'Automated performance monitoring and optimization tasks',
        relayedFrom: 'System',
        timeReceived: 'Continuous'
      },
      {
        id: '11',
        title: 'Security Scan Pipeline',
        description: 'Automated security vulnerability detection and reporting',
        relayedFrom: 'System',
        timeReceived: 'Running'
      }
    ],
    recentHandoffs: [
      {
        id: '9',
        title: 'Deploy Ready Package',
        description: 'Automated build validation and deployment preparation',
        relayedTo: 'Elliott',
        timeHandedOff: '2h ago'
      },
      {
        id: '10',
        title: 'Processed Analytics Report',
        description: 'Auto-generated insights from user behavior data',
        relayedTo: 'Yazide',
        timeHandedOff: '15 min ago'
      }
    ]
  }
};

export default function TaskManager() {
  const [message, setMessage] = useState('');
  const [focusedUser, setFocusedUser] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'focused'>('overview');

  useEffect(() => {
    // Simulate relay handoffs and progress updates
    const interval = setInterval(() => {
      Object.keys(relayWorkflows).forEach(user => {
        const workflow = relayWorkflows[user as keyof typeof relayWorkflows];
        if (workflow.activeWork && Math.random() < 0.08) {
          // Simulate progress updates
          workflow.activeWork.progress = Math.min(100, workflow.activeWork.progress + Math.floor(Math.random() * 3));
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

  const handleUserFocus = (userName: string) => {
    if (focusedUser === userName) {
      setFocusedUser(null);
      setViewMode('overview');
    } else {
      setFocusedUser(userName);
      setViewMode('focused');
    }
  };

  const renderRelayLane = (userName: string, isExpanded: boolean = false) => {
    const workflow = relayWorkflows[userName as keyof typeof relayWorkflows];
    const user = users.find(u => u.name === userName);
    const isRelAI = userName === 'RelAI';
    
    return (
      <div className={`${isExpanded ? 'w-full max-w-5xl' : 'min-w-80 max-w-80'} transition-all duration-300`}>
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
                <Card key={item.id} className="backdrop-blur-xl bg-glass-frosted rounded-xl p-4 border border-glass-border hover:bg-glass-bg transition-all duration-200 relative">
                  
                  {/* Queue position indicator */}
                  <div className="absolute -left-3 top-4 w-6 h-6 bg-status-waiting text-white rounded-full flex items-center justify-center text-xs font-medium">
                    {index + 1}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <h5 className="text-foreground font-medium text-sm leading-tight">
                        {item.title}
                      </h5>
                      <span className="text-xs text-muted-foreground">{item.timeReceived}</span>
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
                <Card key={item.id} className="backdrop-blur-xl bg-glass-frosted rounded-xl p-3 border border-glass-border opacity-60 relative">
                  
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
                        <span>{item.relayedTo}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">{item.timeHandedOff}</div>
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
    <div className="min-h-screen bg-gradient-enterprise">
      {/* Clean enterprise background */}

      <div className="relative z-10 h-screen flex flex-col">
        {/* Header */}
        <div className="p-6 pb-4">
          <div className="flex items-center justify-between animate-slide-up">
            <div>
              <h1 className="text-2xl font-semibold text-foreground mb-1">
                {viewMode === 'focused' && focusedUser ? `${focusedUser} Relay Lane` : 'Relay Command Center'}
              </h1>
              <p className="text-muted-foreground text-sm">
                {viewMode === 'focused' ? 'Individual lane focus' : 'Live handoff monitoring'}
              </p>
            </div>
            
            {viewMode === 'overview' && (
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <div>Active: {Object.values(relayWorkflows).filter(w => w.activeWork).length}</div>
                <div>•</div>
                <div>In Queue: {Object.values(relayWorkflows).reduce((acc, w) => acc + w.incoming.length, 0)}</div>
              </div>
            )}
          </div>
        </div>

        {/* Relay Lanes */}
        <div className="flex-1 overflow-hidden px-6 pb-20">
          <div className="h-full overflow-x-auto">
            <div className={`flex ${viewMode === 'focused' ? 'justify-center' : 'space-x-6'} h-full min-w-max`}>
              {viewMode === 'focused' && focusedUser ? (
                renderRelayLane(focusedUser, true)
              ) : (
                users.map(user => renderRelayLane(user.name, false))
              )}
            </div>
          </div>
        </div>

        {/* Enhanced Command Center Toolbar */}
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
          <div className="backdrop-blur-xl bg-glass-bg rounded-2xl px-6 py-3 border border-glass-border shadow-lg">
            <div className="flex items-center space-x-1">
              {/* Profile Switcher with Active State */}
              {users.map((user) => (
                <Button
                  key={user.id}
                  variant="ghost"
                  size="sm"
                  onClick={() => handleUserFocus(user.name)}
                  className={`
                    ${focusedUser === user.name 
                      ? 'bg-glass-frosted ring-2 ring-border scale-110 h-10 px-4' 
                      : 'hover:bg-glass-frosted h-8 px-3'
                    } 
                    text-foreground flex items-center space-x-2 rounded-xl transition-all duration-200
                    ${user.name === 'RelAI' ? 'border border-status-relai/30' : ''}
                  `}
                >
                  <Avatar className={`${focusedUser === user.name ? 'w-6 h-6' : 'w-5 h-5'} ${user.name === 'RelAI' ? 'ring-1 ring-status-relai/50' : ''}`}>
                    <AvatarImage src={user.avatar} alt={user.name} />
                    <AvatarFallback className={`text-xs ${user.name === 'RelAI' ? 'bg-status-relai/20 text-status-relai' : 'bg-muted'}`}>
                      {user.name === 'RelAI' ? <Bot className="w-3 h-3" /> : user.name[0]}
                    </AvatarFallback>
                  </Avatar>
                  <span className={`${focusedUser === user.name ? 'text-sm font-semibold' : 'text-xs font-medium'}`}>
                    {user.name}
                  </span>
                  {relayWorkflows[user.name as keyof typeof relayWorkflows]?.activeWork && (
                    <div className={`w-1.5 h-1.5 ${user.name === 'RelAI' ? 'bg-status-relai' : 'bg-status-active'} rounded-full animate-pulse`} />
                  )}
                  {user.name === 'RelAI' && focusedUser !== user.name && (
                    <Zap className="w-3 h-3 text-status-relai" />
                  )}
                </Button>
              ))}
              
              <div className="w-px h-6 bg-border mx-3" />
              
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
                    h-7 px-3 rounded-md text-xs font-medium transition-all
                  `}
                >
                  All Lanes
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className={`
                    ${viewMode === 'focused' && focusedUser
                      ? 'bg-background shadow-sm text-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                    } 
                    h-7 px-3 rounded-md text-xs font-medium transition-all
                  `}
                >
                  Focus
                </Button>
              </div>
              
              <div className="w-px h-6 bg-border mx-3" />
              
              {/* Quick Actions */}
              <Button
                variant="ghost"
                size="sm"
                className="text-foreground hover:bg-glass-frosted h-8 px-3 rounded-xl flex items-center space-x-2"
              >
                <Bot className="w-3 h-3" />
                <span className="text-xs">Relay Chat</span>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}