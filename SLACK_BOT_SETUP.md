# Slack Bot Integration Setup

This guide will help you set up the Slack bot integration for the RelAI application.

## Prerequisites

1. A Slack workspace where you have admin permissions
2. An OpenAI API key
3. Python environment with the required dependencies

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your_bot_token_here
SLACK_APP_TOKEN=xapp-your_app_token_here
SLACK_DEFAULT_CHANNEL=general

# Existing Auth Configuration (if using)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=your_jwt_secret_key
FRONTEND_URL=http://localhost:3000
```

## Slack App Setup

### 1. Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Name your app (e.g., "RelAI TaskPilot")
5. Select your workspace

### 2. Configure Bot Token Scopes

1. Go to "OAuth & Permissions" in the sidebar
2. Under "Scopes" > "Bot Token Scopes", add:
   - `chat:write` - Send messages to channels
   - `users:read` - Read user information
   - `users:read.email` - Read user email addresses

### 3. Install the App

1. Go to "Install App" in the sidebar
2. Click "Install to Workspace"
3. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 4. Configure Socket Mode (Optional)

For real-time features:

1. Go to "Basic Information" in the sidebar
2. Under "App-Level Tokens", click "Generate Token and Scopes"
3. Name it "socket-token"
4. Add the `connections:write` scope
5. Copy the generated token (starts with `xapp-`)

### 5. Event Subscriptions (Optional)

For real-time message handling:

1. Go to "Event Subscriptions" in the sidebar
2. Enable events
3. Add bot events:
   - `message.channels` - Messages in public channels
   - `message.im` - Direct messages

## Running the Application

### Backend

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   python main.py
   ```

The server will run on `http://localhost:8000`

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Navigate to the "Slack Bot" page using the navigation
3. Enter a task description in natural language
4. The AI will parse the task and optionally send it to Slack

### Example Tasks

- "Remind Alex to review Q3 numbers by Friday and summarize the response"
- "Ask Sarah to prepare the presentation for next Monday"
- "Tell John to update the documentation by tomorrow"

## Features

- **Task Parsing**: Uses OpenAI to parse natural language into structured tasks
- **Slack Integration**: Sends parsed tasks to Slack with user mentions
- **Real-time Status**: Shows connection status and configuration
- **Flexible Output**: Can parse tasks without sending to Slack

## Troubleshooting

### Common Issues

1. **"Slack connection failed"**
   - Check that your bot token is correct
   - Ensure the bot has the required permissions
   - Verify the bot is installed in your workspace

2. **"OpenAI API error"**
   - Verify your OpenAI API key is correct
   - Check your OpenAI account has sufficient credits

3. **"User not found in Slack"**
   - The bot can only mention users who are in the same workspace
   - Ensure the user's name matches their Slack display name

### Debug Mode

To run the Slack bot in debug mode:

```bash
cd slackBot
python main.py
```

This will run the standalone Slack bot with console output for debugging. 