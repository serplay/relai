import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Bot, ArrowRight, Zap, Clock, Users, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';
import { User } from '@/services/relaiApi';

interface RelAISidebarProps {
  users: User[];
  workflows: Record<string, any>;
  focusedUser: string | null;
  onTaskAction: (action: string, taskId: string, data?: any) => void;
}

export default function RelAISidebar({ users, workflows, focusedUser, onTaskAction }: RelAISidebarProps) {
  const [currentAdvice, setCurrentAdvice] = useState(0);
  
  const getCurrentTask = () => {
    if (focusedUser && workflows[focusedUser]) {
      return workflows[focusedUser].activeWork;
    }
    
    // Find any user with active work
    for (const [userId, workflow] of Object.entries(workflows) as [string, any][]) {
      if (workflow.activeWork) {
        const user = users.find(u => u.id === userId);
        return { ...workflow.activeWork, owner: userId, ownerName: user?.name };
      }
    }
    return null;
  };

  const getNextSteps = (task: any) => {
    if (!task) return [];
    
    const taskOwner = task.owner || focusedUser;
    const workflow = workflows[taskOwner];
    
    const steps = [];
    
    if (task.progress >= 80) {
      steps.push({
        type: 'complete',
        icon: CheckCircle,
        title: 'Ready to Complete',
        description: `This task is ${task.progress}% done and ready to be marked complete`,
        action: 'complete',
        confidence: 'high'
      });
      
      // Show what happens next
      const nextInQueue = workflow?.incoming[0];
      if (nextInQueue) {
        steps.push({
          type: 'next',
          icon: ArrowRight,
          title: 'Next Up',
          description: `"${nextInQueue.title}" will automatically become active`,
          confidence: 'medium'
        });
      } else {
        steps.push({
          type: 'idle',
          icon: Clock,
          title: 'Queue Empty',
          description: 'No tasks in queue - perfect time for new assignments',
          confidence: 'low'
        });
      }
    } else if (task.progress < 30) {
      // Suggest handoff if stuck
      const availableUsers = users.filter(u => u.id !== taskOwner && u.name !== 'RelAI');
      const idleUsers = availableUsers.filter(u => !workflows[u.id]?.activeWork);
      
      if (idleUsers.length > 0) {
        steps.push({
          type: 'handoff',
          icon: Users,
          title: 'Consider Handoff',
          description: `${idleUsers[0].name} is available and could help accelerate this task`,
          action: 'handoff',
          targetUser: idleUsers[0].id,
          confidence: 'medium'
        });
      } else {
        steps.push({
          type: 'focus',
          icon: TrendingUp,
          title: 'Focus Time',
          description: 'This task needs concentrated effort to move forward',
          confidence: 'medium'
        });
      }
    } else {
      steps.push({
        type: 'progress',
        icon: TrendingUp,
        title: 'Making Progress',
        description: `On track - ${100 - task.progress}% remaining to completion`,
        confidence: 'high'
      });
      
      if (task.progress >= 60) {
        steps.push({
          type: 'estimate',
          icon: Clock,
          title: 'Estimated Completion',
          description: `Should be ready for handoff in ${task.estimatedHandoff}`,
          confidence: 'medium'
        });
      }
    }
    
    return steps;
  };

  const getRelAIQuestions = (task: any) => {
    if (!task) {
      return [
        "Hey! I don't see any active tasks right now. Want me to help assign some work?",
        "Everything looks quiet. Perfect time to plan the next sprint - need any suggestions?",
        "No active tasks detected. Should I help optimize the workflow queue?"
      ];
    }
    
    const questions = [];
    
    if (task.progress >= 80) {
      questions.push(
        `"${task.title}" looks almost done! Ready to mark it complete?`,
        `This task is ${task.progress}% finished. What's blocking the final ${100 - task.progress}%?`,
        `Great progress on "${task.title}"! Should I prepare the handoff to the next person?`
      );
    } else if (task.progress < 30) {
      questions.push(
        `"${task.title}" seems to be at ${task.progress}%. What's the main challenge right now?`,
        `This task looks stuck at ${task.progress}%. Need me to find someone who can help?`,
        `"${task.title}" could use a boost. Want me to suggest the best person to handoff to?`
      );
    } else {
      questions.push(
        `How's "${task.title}" going? I see it's at ${task.progress}% - anything I can help with?`,
        `"${task.title}" is making good progress! What's the next milestone?`,
        `Looking good on "${task.title}"! Is the ${task.estimatedHandoff} estimate still accurate?`
      );
    }
    
    return questions;
  };

  const currentTask = getCurrentTask();
  const nextSteps = getNextSteps(currentTask);
  const questions = getRelAIQuestions(currentTask);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentAdvice((prev) => (prev + 1) % questions.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [questions.length]);

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'text-green-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-gray-500';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className="w-80 h-full bg-background border-l border-border flex flex-col">
      {/* RelAI Header */}
      <div className="p-4 border-b border-border bg-gradient-to-r from-primary/5 to-purple-500/5">
        <div className="flex items-center space-x-3">
          <Avatar className="w-10 h-10 ring-2 ring-primary/20">
            <AvatarFallback className="bg-primary/10 text-primary">
              <Bot className="w-5 h-5" />
            </AvatarFallback>
          </Avatar>
          <div>
            <h3 className="font-semibold text-foreground">RelAI Assistant</h3>
            <p className="text-xs text-muted-foreground">Workflow Intelligence</p>
          </div>
          <div className="ml-auto">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Current Task Focus */}
      {currentTask && (
        <div className="p-4 border-b border-border">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm text-foreground">Current Focus</h4>
              <Badge variant="secondary" className="text-xs">
                {currentTask.owner || focusedUser}
              </Badge>
            </div>
            
            <Card className="p-3 bg-muted/50">
              <h5 className="font-medium text-sm mb-2 text-foreground">{currentTask.title}</h5>
              <p className="text-xs text-muted-foreground mb-3">{currentTask.description}</p>
              
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium text-foreground">{currentTask.progress}%</span>
                </div>
                <Progress value={currentTask.progress} className="h-2" />
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* RelAI Question */}
      <div className="p-4 border-b border-border bg-accent/20">
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Bot className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-foreground">RelAI asks:</span>
          </div>
          
          <div className="bg-background/50 rounded-lg p-3 border border-border/50">
            <p className="text-sm text-foreground leading-relaxed">
              {questions[currentAdvice]}
            </p>
          </div>
          
          <div className="flex justify-center">
            <div className="flex space-x-1">
              {questions.map((_, index) => (
                <div
                  key={index}
                  className={`w-1.5 h-1.5 rounded-full transition-colors ${
                    index === currentAdvice ? 'bg-primary' : 'bg-muted-foreground/30'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Next Steps Prediction */}
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="space-y-4">
          <h4 className="font-medium text-sm text-foreground flex items-center space-x-2">
            <Zap className="w-4 h-4 text-primary" />
            <span>What Happens Next</span>
          </h4>
          
          <div className="space-y-3">
            {nextSteps.map((step, index) => {
              const IconComponent = step.icon;
              return (
                <Card key={index} className="p-3 hover:bg-muted/50 transition-colors">
                  <div className="flex items-start space-x-3">
                    <div className={`mt-0.5 ${getConfidenceColor(step.confidence)}`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center justify-between">
                        <h5 className="font-medium text-sm text-foreground">{step.title}</h5>
                        <div className={`w-2 h-2 rounded-full ${
                          step.confidence === 'high' ? 'bg-green-500' :
                          step.confidence === 'medium' ? 'bg-yellow-500' : 'bg-gray-400'
                        }`} />
                      </div>
                      <p className="text-xs text-muted-foreground">{step.description}</p>
                      
                      {step.action && (
                        <Button
                          size="sm"
                          variant={step.type === 'complete' ? 'default' : 'outline'}
                          className="text-xs h-7 w-full"
                          onClick={() => onTaskAction(step.action, currentTask.id, { targetUser: step.targetUser })}
                        >
                          {step.type === 'complete' ? '✅ Complete Task' : 
                           step.type === 'handoff' ? `➡️ Handoff to ${users.find(u => u.id === step.targetUser)?.name}` : 
                           'Take Action'}
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
          
          {nextSteps.length === 0 && (
            <Card className="p-4 text-center border-dashed">
              <Bot className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">
                I'll analyze workflow patterns once there's an active task to predict next steps.
              </p>
            </Card>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-t border-border bg-muted/20">
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" size="sm" className="text-xs">
            <TrendingUp className="w-3 h-3 mr-1" />
            Optimize
          </Button>
          <Button variant="outline" size="sm" className="text-xs">
            <Users className="w-3 h-3 mr-1" />
            Rebalance
          </Button>
        </div>
      </div>
    </div>
  );
}