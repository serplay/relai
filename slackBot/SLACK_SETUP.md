# Slack Setup Guide for TaskPilot AI

This guide will help you set up the correct Slack tokens to resolve the "not_allowed_token_type" error and enable user mentions.

## 🚨 Error: "not_allowed_token_type"

This error occurs when you're using the wrong type of Slack token. You need **two different tokens**:

1. **Bot User OAuth Token** (starts with `xoxb-`)
2. **App-Level Token** (starts with `xapp-`)

## 📋 Step-by-Step Setup

### Step 1: Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Name your app (e.g., "TaskPilot AI")
5. Select your workspace

### Step 2: Configure App Permissions

1. In your app, go to **"OAuth & Permissions"**
2. Under **"Scopes"** > **"Bot Token Scopes"**, add:
   - `chat:write` - Send messages
   - `channels:read` - Read channel info
   - `app_mentions:read` - Read mentions
   - `channels:history` - Read channel messages
   - `users:read` - **NEW: Read user info for mentions**

### Step 3: Get Bot User OAuth Token

1. In **"OAuth & Permissions"**
2. Click **"Install to Workspace"**
3. Authorize the app
4. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)
5. This is your `SLACK_BOT_TOKEN`

### Step 4: Create App-Level Token

1. Go to **"Basic Information"**
2. Scroll down to **"App-Level Tokens"**
3. Click **"Generate Token and Scopes"**
4. Name it (e.g., "socket-mode")
5. Add scope: `connections:write`
6. Click **"Generate"**
7. Copy the token (starts with `xapp-`)
8. This is your `SLACK_APP_TOKEN`

### Step 5: Enable Socket Mode

1. Go to **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** to ON
3. Select your app-level token from Step 4
4. Save changes

### Step 6: Configure Environment Variables

Add these to your `.env` file:

```bash
# Bot User OAuth Token (from Step 3)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# App-Level Token (from Step 4)
SLACK_APP_TOKEN=xapp-your-app-token-here

# Default channel (optional)
SLACK_DEFAULT_CHANNEL=general
```

### Step 7: Add Bot to Channel

1. In Slack, go to the channel you want to use
2. Type: `/invite @YourBotName`
3. Or add the bot manually through channel settings

## 🔍 Token Validation

The system will now validate your tokens:

- ✅ `SLACK_BOT_TOKEN` should start with `xoxb-`
- ✅ `SLACK_APP_TOKEN` should start with `xapp-`

## 👤 User Mentions Feature

The bot can now:
- ✅ **Look up users** by their display name or real name
- ✅ **Mention users** with proper `@username` format
- ✅ **Send notifications** directly to specific people

**Example**: When you say "Remind Alex to review the report", the bot will:
1. Find Alex in your Slack workspace
2. Send a message with `<@U1234567890>` (Alex's user ID)
3. Alex will get a notification

## 🧪 Test Your Setup

```bash
# Test connection
python main.py

# Or run in Socket Mode
python main.py socket
```

## ❌ Common Issues

### "not_allowed_token_type"
- **Cause**: Using wrong token type
- **Fix**: Make sure you have both `xoxb-` and `xapp-` tokens

### "invalid_auth"
- **Cause**: Token is incorrect or expired
- **Fix**: Regenerate tokens in Slack app settings

### "channel_not_found"
- **Cause**: Bot not added to channel
- **Fix**: Invite bot to channel with `/invite @BotName`

### "missing_scope"
- **Cause**: Bot doesn't have required permissions
- **Fix**: Add missing scopes in OAuth & Permissions
- **For user mentions**: Make sure `users:read` scope is added

### "User not found"
- **Cause**: User name doesn't match Slack display name
- **Fix**: Use the exact display name or real name from Slack

## 🔗 Useful Links

- [Slack API Apps](https://api.slack.com/apps)
- [Socket Mode Documentation](https://api.slack.com/apis/connections/socket)
- [Bot Token Scopes](https://api.slack.com/scopes)
- [User Lookup API](https://api.slack.com/methods/users.list)

---

*Follow these steps carefully and your TaskPilot AI should work with Slack and mention users!* 