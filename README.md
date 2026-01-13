# Chiron 🏛️

**Your AI Fitness Mentor**

Chiron integrates your workout data from TrueCoach, nutrition tracking from MyFitnessPal, and Google's Gemini AI to provide intelligent, personalized fitness insights. Named after the wise centaur who trained Greek heroes.

## Features

- 🏋️ **Workout Tracking**: Automatic sync with TrueCoach
- 🍎 **Nutrition Tracking**: Integration with MyFitnessPal
- 🤖 **AI Insights**: Powered by Google Gemini with function calling
- 📊 **Trend Analysis**: Track your progress over time
- 🔄 **Auto-Sync**: Background data synchronization every 30 minutes
- 🔐 **Secure OAuth**: Safe connection to your fitness accounts

## Architecture

```
┌─────────────────┐
│  TrueCoach API  │──┐
└─────────────────┘  │
                     ├──> ┌────────────────────┐
┌─────────────────┐  │    │  Chiron API        │
│ MyFitnessPal    │──┼───>│  (FastAPI)         │
└─────────────────┘  │    │  + PostgreSQL      │
                     │    └────────────────────┘
┌─────────────────┐  │              │
│  Gemini Chat    │──┘              │
│  (You chat here)│<────────────────┘
└─────────────────┘   Function calls API
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- TrueCoach account & API credentials
- MyFitnessPal account
- Google Gemini API key

### Installation

```bash
# Clone and navigate
cd chiron

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python scripts/init_db.py

# Run the server
uvicorn main:app --reload
```

### Configuration

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/chiron
GEMINI_API_KEY=your_gemini_key
TRUECOACH_CLIENT_ID=your_truecoach_client_id
TRUECOACH_CLIENT_SECRET=your_truecoach_secret
MFP_USERNAME=your_mfp_username
MFP_PASSWORD=your_mfp_password
API_SECRET_KEY=your_random_secret_key
```

## Usage

### 1. Connect Your Accounts

Visit `http://localhost:8000` and connect your TrueCoach and MyFitnessPal accounts via OAuth.

### 2. Use the Gemini Client

```python
from chiron_client import ChironChat

# Initialize
chat = ChironChat(user_id="your_user_id", api_key="your_api_key")

# Ask questions - Gemini automatically pulls your data!
response = await chat.send_message("How am I doing today?")
print(response)

response = await chat.send_message("Should I increase my calories?")
print(response)

response = await chat.send_message("Compare this week to last week")
print(response)
```

### 3. API Endpoints

- `GET /api/v1/fitness/{user_id}/today` - Get today's data
- `GET /api/v1/fitness/{user_id}/week` - Get this week's data
- `GET /api/v1/fitness/{user_id}/trends` - Get trends over time
- `POST /api/v1/chat` - Chat with AI (with context)

## Deployment

### Render

```bash
# Push to GitHub
git add .
git commit -m "Initial Chiron setup"
git push origin main

# In Render dashboard:
# 1. New Web Service
# 2. Connect your GitHub repo
# 3. Add PostgreSQL database
# 4. Set environment variables
# 5. Deploy!
```

Configuration is in `render.yaml`.

## Project Structure

```
chiron/
├── main.py                 # FastAPI application
├── requirements.txt
├── render.yaml            # Render deployment config
├── .env.example
├── models/
│   ├── __init__.py
│   ├── user.py           # User model
│   ├── workout.py        # Workout data model
│   └── nutrition.py      # Nutrition data model
├── services/
│   ├── __init__.py
│   ├── truecoach.py      # TrueCoach API client
│   ├── mfp.py            # MyFitnessPal integration
│   └── gemini.py         # Gemini AI client
├── api/
│   ├── __init__.py
│   └── routes.py         # API endpoints
├── tasks/
│   ├── __init__.py
│   └── sync.py           # Background sync tasks
├── database/
│   ├── __init__.py
│   └── db.py             # Database connection
├── scripts/
│   └── init_db.py        # Database initialization
└── chiron_client.py      # Python client for end users
```

## Technologies

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Robust database
- **SQLAlchemy** - ORM
- **Google Gemini** - AI with function calling
- **APScheduler** - Background task scheduling
- **OAuth 2.0** - Secure authentication

## Roadmap

- [ ] TrueCoach integration
- [ ] MyFitnessPal integration
- [ ] Basic Gemini chat
- [ ] Trend analysis
- [ ] Mobile app wrapper
- [ ] Coach sharing features
- [ ] Workout recommendations
- [ ] Nutrition optimization suggestions

## Contributing

Pull requests welcome! This is a personal project but happy to collaborate.

## License

MIT License - See LICENSE file

---

*Train like a hero* 🏛️
