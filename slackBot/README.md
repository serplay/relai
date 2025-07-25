# TaskPilot AI

TaskPilot AI is a simple Slack bot that understands natural language task requests and parses them using LLM technology.

## 🚀 Features

- **Natural Language Parsing**: Understands task requests using OpenAI API
- **Slack Integration**: Sends parsed tasks to Slack using Socket Mode
- **Real-time Events**: Listens for Slack events in Socket Mode
- **Simple & Lightweight**: Focused on core functionality

## 🏗️ Architecture

- **LLM Parser**: Extracts structured task data from natural language
- **Slack Interface**: Handles user input and Slack integration via Socket Mode

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   # Copy example environment file
   cp example.env .env
   
   # Edit with your actual values
   nano .env
   ```

3. **Run the application:**
   ```bash
   # Interactive mode (single task)
   python main.py
   
   # Socket Mode (real-time Slack events)
   python main.py socket
   ```

## 📖 Usage

### Interactive Mode
```bash
python main.py
# Enter: "Remind Sarah to send the draft next Monday and summarize her reply"
```

### Socket Mode (Real-time)
```bash
python main.py socket
# Listens for Slack events and processes them in real-time
```

## 🧠 Task Parsing

The system can parse various natural language formats:

- **"Remind [Name] to [task] [date] and [action]"**
- **"Ask [Name] to [task] [date]"**
- **"Tell [Name] to [task] [date]"**

**Example inputs:**
- "Remind Sarah to send the draft next Monday and summarize her reply"
- "Ask Alex to review Q3 numbers today and confirm completion"
- "Tell John to prepare the presentation for tomorrow"

## 🔌 Socket Mode

Socket Mode enables real-time communication with Slack:

- **Real-time Events**: Listen for messages, reactions, and other Slack events
- **No Webhooks**: No need to expose public endpoints
- **Secure**: Uses WebSocket connection with app-level authentication
- **Scalable**: Handles multiple events simultaneously

## 🔧 Project Structure

```
TaskPilot AI/
├── main.py              # Entry point (interactive + socket modes)
├── llm_parser.py        # Natural language parsing (OpenAI + fallback)
├── slack_interface.py   # Slack integration (Socket Mode + Web API)
├── requirements.txt    # Python dependencies
├── example.env         # Environment variables template
└── README.md          # This file
```

## 🎯 Current Status

✅ **Completed Features:**
- Natural language task parsing (OpenAI + fallback)
- Slack integration via Socket Mode
- Real-time event handling
- User input handling

🔄 **Ready for Enhancement:**
- Enhanced LLM parsing
- Advanced Slack app features
- Task scheduling
- Message threading

## 🚀 Next Steps

1. **Configure Slack App** with Socket Mode enabled
2. **Add slash commands** for direct Slack interaction
3. **Implement message threading** for task conversations
4. **Add task scheduling** functionality

## 🔑 Required Environment Variables

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Slack (Socket Mode)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_DEFAULT_CHANNEL=general
```

---

*Simple TaskPilot AI - LLM + Slack Bot with Socket Mode* 