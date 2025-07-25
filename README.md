# Google OAuth FastAPI Setup

## Project Structure

```
relai/
├── main.py                 # Main FastAPI application
├── auth/                   # Authentication module
│   ├── __init__.py
│   ├── models.py          # Pydantic models for auth
│   ├── jwt_handler.py     # JWT token handling
│   ├── google_oauth.py    # Google OAuth integration
│   └── routes.py          # Auth API routes
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Prerequisites

1. Create a Google Cloud Project and enable the Google+ API
2. Create OAuth 2.0 credentials (Client ID and Client Secret)
3. Set up authorized redirect URIs

## Setup Instructions

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your Google OAuth credentials:
   - `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret
   - `JWT_SECRET_KEY`: A secure random string for JWT signing
   - `FRONTEND_URL`: Your frontend application URL

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## API Endpoints

### Authentication Flow

1. **GET /auth/google/url** - Get Google OAuth authorization URL
2. **POST /auth/google/token** - Exchange OAuth code for JWT token
3. **GET /auth/me** - Get current user information (requires JWT token)
4. **GET /protected** - Example protected route (requires JWT token)

### Usage Example

1. Get the Google OAuth URL:
   ```bash
   curl http://localhost:8000/auth/google/url
   ```

2. Redirect user to the returned `auth_url`

3. After user authorization, Google redirects back with a `code` parameter

4. Exchange the code for a token:
   ```bash
   curl -X POST http://localhost:8000/auth/google/token \
     -H "Content-Type: application/json" \
     -d '{"code": "YOUR_CODE", "redirect_uri": "YOUR_REDIRECT_URI"}'
   ```

5. Use the returned JWT token in Authorization header:
   ```bash
   curl http://localhost:8000/auth/me \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API or Google Identity API
4. Go to "Credentials" and create OAuth 2.0 Client IDs
5. Add your redirect URIs (e.g., `http://localhost:3000/auth/callback` for development)
6. Copy the Client ID and Client Secret to your `.env` file

## Security Notes

- Use HTTPS in production
- Configure CORS properly for your domain
- Keep your JWT secret key secure
- Set appropriate token expiration times
- Validate redirect URIs properly
