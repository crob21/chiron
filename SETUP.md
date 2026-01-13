# Chiron Setup Guide

Complete guide to getting Chiron up and running.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 13 or higher
- Google Gemini API key
- TrueCoach account (optional for testing)
- MyFitnessPal account (optional for testing)

## Local Development Setup

### 1. Clone and Install

```bash
cd /path/to/chiron
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

```bash
# Create database
createdb chiron

# Or using psql
psql -U postgres
CREATE DATABASE chiron;
\q
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/chiron
GEMINI_API_KEY=your_gemini_api_key
API_SECRET_KEY=your_random_secret_key
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Run the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Or using Python
python main.py
```

Visit http://localhost:8000 to see it running!

## Docker Setup (Easier!)

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your keys

# Start everything
docker-compose up

# Stop
docker-compose down
```

## Getting API Keys

### Google Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy it to your `.env` file

### TrueCoach OAuth

1. Log into TrueCoach
2. Go to Settings → API
3. Create a new OAuth application
4. Set redirect URI: `http://localhost:8000/auth/truecoach/callback`
5. Copy Client ID and Secret to `.env`

### MyFitnessPal

Currently uses username/password. Add to `.env`:

```env
MFP_USERNAME=your_username
MFP_PASSWORD=your_password
```

Note: You may want to use the Python `myfitnesspal` package instead.

## Creating Your First User

You can manually create a user in the database or via API:

```python
from database.db import SessionLocal
from models import User

db = SessionLocal()
user = User(
    email="your@email.com"
)
db.add(user)
db.commit()

print(f"User ID: {user.id}")
print(f"API Key: {user.api_key}")
```

## Using the Chiron Client

```python
import asyncio
from chiron_client import ChironChat

async def main():
    chat = ChironChat(
        user_id="your_user_id",
        api_key="your_api_key",
        chiron_api_base="http://localhost:8000/api/v1"
    )

    response = await chat.send_message("How am I doing today?")
    print(response)

asyncio.run(main())
```

## Testing the API

### Using cURL

```bash
# Get today's data
curl "http://localhost:8000/api/v1/fitness/USER_ID/today?api_key=YOUR_API_KEY"

# Get this week
curl "http://localhost:8000/api/v1/fitness/USER_ID/week?api_key=YOUR_API_KEY"

# Chat
curl -X POST "http://localhost:8000/api/v1/chat?api_key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "How am I doing?", "user_id": "USER_ID"}'
```

### Using Python requests

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/fitness/YOUR_USER_ID/today",
    params={"api_key": "YOUR_API_KEY"}
)
print(response.json())
```

## Deployment to Render

### 1. Push to GitHub

```bash
cd chiron
git init
git add .
git commit -m "Initial Chiron setup"
git remote add origin https://github.com/yourusername/chiron.git
git push -u origin main
```

### 2. Create Render Account

Visit https://render.com and sign up.

### 3. Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Render will detect `render.yaml` automatically
4. Set environment variables:
   - `GEMINI_API_KEY`
   - `TRUECOACH_CLIENT_ID`
   - `TRUECOACH_CLIENT_SECRET`
   - `MFP_USERNAME`
   - `MFP_PASSWORD`
5. Click "Create Web Service"

### 4. Create Database

Render will automatically create the PostgreSQL database based on `render.yaml`.

### 5. Update Redirect URIs

Update your TrueCoach OAuth redirect URI to:
```
https://your-app-name.onrender.com/auth/truecoach/callback
```

## Troubleshooting

### Database Connection Errors

```bash
# Check PostgreSQL is running
pg_isready

# Check connection string format
# Should be: postgresql://user:password@host:port/database
```

### Import Errors

```bash
# Make sure you're in the venv
which python

# Reinstall dependencies
pip install -r requirements.txt
```

### Gemini API Errors

- Check your API key is valid
- Ensure you have billing enabled (Gemini requires it)
- Check API quotas at https://console.cloud.google.com

### TrueCoach/MyFitnessPal Not Syncing

- Check tokens are valid
- Look at logs: `tail -f logs/chiron.log`
- Manually trigger sync (will add admin endpoint)

## Next Steps

1. Connect your accounts via OAuth
2. Run a manual sync to populate data
3. Test the AI chat
4. Set up monitoring/alerting
5. Customize prompts and insights

## Support

Open an issue on GitHub or check the documentation at `/docs` endpoint.

---

Train like a hero! 🏛️
