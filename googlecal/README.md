# Google Calendar Python Example

## Quick Setup (5 minutes)

### 1. Install dependencies

```bash
pip install google-api-python-client google-auth google-auth-oauthlib
```

### 2. Get Google credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Calendar API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Desktop application**
6. Download the JSON file and rename it to `credentials.json`
7. Put `credentials.json` in the same folder as your Python script

### 3. Run the script

```bash
python google_calendar_example.py
```

### 4. First run

- Your browser will open for Google login
- Grant calendar permissions
- A `token.json` file will be created (saves your login for next time)

## What it does

- Fetches your next 10 upcoming calendar events
- Prints them with date/time and title
- Works with your primary Google Calendar

## Output example

```
Upcoming events:
2024-01-15T10:00:00-08:00: Team Meeting
2024-01-15T14:30:00-08:00: Doctor Appointment
2024-01-16T09:00:00-08:00: Project Review
```
