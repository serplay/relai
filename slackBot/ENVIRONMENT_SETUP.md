# Environment Setup Guide for TaskPilot AI

This guide explains how to configure environment variables for TaskPilot AI to enable LLM parsing and Slack integration.

## 🔧 Environment Variables

### Required for Production

#### OpenAI API (for LLM parsing)
```bash
OPENAI_API_KEY=your_openai_api_key_here
```
- **Purpose**: Enables real LLM parsing instead of fallback pattern matching
- **How to get**: Sign up at [OpenAI Platform](https://platform.openai.com/api-keys)
- **Required for**: Enhanced natural language task parsing

#### Slack Integration
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your_signing_secret
```
- **Purpose**: Enable real Slack bot functionality
- **How to get**: Create a Slack app at [api.slack.com](https://api.slack.com/apps)
- **Required for**: Real-time Slack messaging

### Optional Configuration

#### Application Settings
```bash
# Logging level
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development

# OpenAI Model Configuration
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.1
```

## 📍 Where to Put Environment Variables

### Option 1: .env File (Recommended for Development)
Create a `.env` file in the project root:
```bash
# Create .env file
touch .env

# Add your variables
echo "OPENAI_API_KEY=your_key_here" >> .env
echo "SLACK_BOT_TOKEN=your_token_here" >> .env
```

### Option 2: System Environment Variables
```bash
# macOS/Linux
export OPENAI_API_KEY="your_key_here"
export SLACK_BOT_TOKEN="your_token_here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your_key_here
set SLACK_BOT_TOKEN=your_token_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_key_here"
$env:SLACK_BOT_TOKEN="your_token_here"
```

## 🔒 Security Best Practices

1. **Never commit .env files to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.env" >> .gitignore
   ```

2. **Use different keys for development and production**

3. **Rotate keys regularly**

## 🚀 Quick Start

1. **Copy the example environment file:**
   ```bash
   cp example.env .env
   ```

2. **Edit .env with your actual values:**
   ```bash
   nano .env
   ```

3. **Test the configuration:**
   ```bash
   python main.py
   ```

## 🔍 Testing Environment Variables

Add this to your Python code to test:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Test if variables are loaded
print(f"OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
print(f"Slack Bot Token: {'✅ Set' if os.getenv('SLACK_BOT_TOKEN') else '❌ Missing'}")
```

## 📋 Environment Checklist

- [ ] OpenAI API key configured
- [ ] Slack app tokens configured
- [ ] .env file added to .gitignore
- [ ] Environment variables tested
- [ ] Application runs without errors

---

*For production deployment, consider using a secrets management service like AWS Secrets Manager or HashiCorp Vault.* 