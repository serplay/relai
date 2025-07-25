# Fix Google OAuth "App in Testing" Error

## Problem

Getting this error: _"App is currently being tested and can only be accessed by developer-approved testers"_

## Solution: Add Test Users

### Step 1: Go to OAuth Consent Screen

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **OAuth consent screen**

### Step 2: Add Test Users

1. Scroll down to **"Test users"** section
2. Click **"+ ADD USERS"**
3. Enter email addresses (one per line):
   ```
   your.email@gmail.com
   another.tester@gmail.com
   ```
4. Click **"Save"**

### Step 3: Try Again

- Run your Python script again
- The added email addresses can now authenticate

## Alternative: Publish App (Advanced)

If you want public access:

1. In OAuth consent screen → **"PUBLISH APP"**
2. Complete Google's verification process (takes time)
3. App becomes available to all users

## Quick Test

```bash
python google_calendar_example.py
```

Should now work with the test email addresses you added!
