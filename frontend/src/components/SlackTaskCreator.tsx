import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Send, CheckCircle, AlertCircle } from 'lucide-react';

interface TaskResponse {
  success: boolean;
  parsed_task?: {
    recipient: string;
    task: string;
    due_date: string;
    response_required: boolean;
    output?: string;
  };
  message: string;
  slack_sent: boolean;
}

const SlackTaskCreator: React.FC = () => {
  const [taskDescription, setTaskDescription] = useState('');
  const [channel, setChannel] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<TaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!taskDescription.trim()) {
      setError('Please enter a task description');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const payload: any = {
        task: taskDescription.trim()
      };

      if (channel.trim()) {
        payload.channel = channel.trim();
      }

      const response = await fetch('/slack-bot/create-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        setResponse(data);
      } else {
        setError(data.detail || 'Failed to create task');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setTaskDescription('');
    setChannel('');
    setResponse(null);
    setError(null);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Send className="h-5 w-5" />
            Create Slack Task
          </CardTitle>
          <CardDescription>
            Enter a natural language task description and it will be sent to Slack as a formatted message.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="task">Task Description</Label>
              <Textarea
                id="task"
                placeholder="e.g., Remind Alex to review Q3 numbers by Friday and provide a summary"
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                className="min-h-[100px]"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="channel">Slack Channel (optional)</Label>
              <Input
                id="channel"
                placeholder="e.g., general, team-updates"
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={isLoading || !taskDescription.trim()}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Task...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Create Task
                  </>
                )}
              </Button>
              <Button type="button" variant="outline" onClick={handleClear} disabled={isLoading}>
                Clear
              </Button>
            </div>
          </form>

          {/* Error Display */}
          {error && (
            <Alert className="mt-4 border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {/* Success Response */}
          {response && (
            <Alert className={`mt-4 ${response.success ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
              <CheckCircle className={`h-4 w-4 ${response.success ? 'text-green-600' : 'text-yellow-600'}`} />
              <AlertDescription className={response.success ? 'text-green-800' : 'text-yellow-800'}>
                {response.message}
              </AlertDescription>
            </Alert>
          )}

          {/* Parsed Task Details */}
          {response?.parsed_task && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="text-sm">Parsed Task Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="font-medium">Recipient:</span>
                    <span className="ml-2">{response.parsed_task.recipient}</span>
                  </div>
                  <div>
                    <span className="font-medium">Due Date:</span>
                    <span className="ml-2">{new Date(response.parsed_task.due_date).toLocaleDateString()}</span>
                  </div>
                </div>
                <div>
                  <span className="font-medium">Task:</span>
                  <span className="ml-2">{response.parsed_task.task}</span>
                </div>
                <div>
                  <span className="font-medium">Response Required:</span>
                  <span className="ml-2">{response.parsed_task.response_required ? 'Yes' : 'No'}</span>
                </div>
                {response.parsed_task.output && (
                  <div>
                    <span className="font-medium">Output Format:</span>
                    <span className="ml-2">{response.parsed_task.output}</span>
                  </div>
                )}
                <div>
                  <span className="font-medium">Slack Status:</span>
                  <span className={`ml-2 ${response.slack_sent ? 'text-green-600' : 'text-red-600'}`}>
                    {response.slack_sent ? 'Sent successfully' : 'Failed to send'}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Example Tasks */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">Example Task Formats</CardTitle>
          <CardDescription>
            Try these natural language formats:
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100" 
                 onClick={() => setTaskDescription("Remind Alex to review Q3 numbers by Friday and provide a summary")}>
              "Remind Alex to review Q3 numbers by Friday and provide a summary"
            </div>
            <div className="p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100"
                 onClick={() => setTaskDescription("Ask Sarah to prepare the monthly report for next Monday")}>
              "Ask Sarah to prepare the monthly report for next Monday"
            </div>
            <div className="p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100"
                 onClick={() => setTaskDescription("Tell John to update the project timeline by tomorrow")}>
              "Tell John to update the project timeline by tomorrow"
            </div>
            <div className="p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100"
                 onClick={() => setTaskDescription("Ask the team to review the new feature proposal by Wednesday")}>
              "Ask the team to review the new feature proposal by Wednesday"
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SlackTaskCreator; 