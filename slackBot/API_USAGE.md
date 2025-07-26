# Slack Bot API Usage

The Slack Bot now provides a simple API endpoint for creating tasks from natural language descriptions.

## Main Endpoint

### POST `/slack-bot/create-task`

Creates a Slack message from a natural language task description.

**Request Body:**
```json
{
  "task": "Remind Alex to review Q3 numbers by Friday and provide a summary",
  "channel": "general"  // optional, defaults to configured channel
}
```

**Response:**
```json
{
  "success": true,
  "parsed_task": {
    "recipient": "Alex",
    "task": "review Q3 numbers",
    "due_date": "2024-01-19T00:00:00",
    "response_required": true,
    "output": "summary"
  },
  "message": "Task created and sent to Slack successfully",
  "slack_sent": true
}
```

## Example Usage

### Python
```python
import requests

def create_task(task_description, channel=None):
    url = "http://localhost:8000/slack-bot/create-task"
    payload = {"task": task_description}
    if channel:
        payload["channel"] = channel
    
    response = requests.post(url, json=payload)
    return response.json()

# Example usage
result = create_task("Ask Sarah to prepare the monthly report by Monday")
print(result)
```

### cURL
```bash
curl -X POST "http://localhost:8000/slack-bot/create-task" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Remind John to update the project timeline by tomorrow"
  }'
```

### JavaScript/Fetch
```javascript
async function createTask(taskDescription, channel = null) {
  const response = await fetch('http://localhost:8000/slack-bot/create-task', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      task: taskDescription,
      channel: channel
    })
  });
  
  return await response.json();
}

// Example usage
createTask("Tell the team to review the new feature proposal by Wednesday")
  .then(result => console.log(result));
```

## Other Endpoints

### GET `/slack-bot/status`
Check if Slack integration is working:
```bash
curl "http://localhost:8000/slack-bot/status"
```

### GET `/slack-bot/config`
Check configuration status:
```bash
curl "http://localhost:8000/slack-bot/config"
```

### POST `/slack-bot/parse-only`
Parse a task without sending to Slack:
```bash
curl -X POST "http://localhost:8000/slack-bot/parse-only" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Remind Alex to review Q3 numbers by Friday"}'
```

## Task Format Examples

The API can handle various natural language formats:

- **"Remind Alex to review Q3 numbers by Friday"**
- **"Ask Sarah to prepare the monthly report for next Monday"**
- **"Tell John to update the project timeline by tomorrow"**
- **"Ask the team to review the new feature proposal by Wednesday"**

## Configuration

Make sure your Slack bot is properly configured with:
- `SLACK_BOT_TOKEN` (xoxb-...)
- `SLACK_APP_TOKEN` (xapp-...)
- `OPENAI_API_KEY` (for natural language parsing)
- `SLACK_DEFAULT_CHANNEL` (default channel for messages)

## Running the Example

Use the provided example script:
```bash
cd slackBot
python example_usage.py
```

This will demonstrate the API with sample tasks and allow interactive testing. 