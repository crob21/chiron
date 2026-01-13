"""Chiron - Your AI Fitness Mentor.

Main FastAPI application with background sync tasks.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging
import uvicorn

from config import get_settings
from database import init_db
from api.routes import router
from tasks import sync_all_users

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI."""
    # Startup
    logger.info("Starting Chiron API...")
    await init_db()

    # Start background sync task
    scheduler.add_job(
        sync_all_users,
        'interval',
        minutes=settings.sync_interval_minutes,
        id='sync_fitness_data'
    )
    scheduler.start()
    logger.info(f"Background sync started (every {settings.sync_interval_minutes} minutes)")

    yield

    # Shutdown
    scheduler.shutdown()
    logger.info("Chiron API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Chiron API",
    description="Your AI Fitness Mentor - Integrating TrueCoach, MyFitnessPal, and Gemini AI",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with basic info."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chiron - Your AI Fitness Mentor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #2c3e50; }
            .hero { font-size: 1.2em; color: #7f8c8d; margin-bottom: 30px; }
            .feature {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .cta {
                background: #3498db;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <h1>🏛️ Chiron</h1>
        <div class="hero">
            Your AI Fitness Mentor - Train Like a Hero
        </div>

        <div class="feature">
            <h3>🏋️ Workout Tracking</h3>
            <p>Automatic sync with TrueCoach for comprehensive workout data</p>
        </div>

        <div class="feature">
            <h3>🍎 Nutrition Tracking</h3>
            <p>Integration with MyFitnessPal for macro and calorie tracking</p>
        </div>

        <div class="feature">
            <h3>🤖 AI Insights</h3>
            <p>Powered by Google Gemini for personalized fitness advice</p>
        </div>

        <h2>Getting Started</h2>
        <ol>
            <li>Connect your TrueCoach account: <a href="/auth/truecoach">Connect</a></li>
            <li>Connect your MyFitnessPal account: <a href="/auth/mfp">Connect</a></li>
            <li>Get your API key from your profile</li>
            <li>Start chatting with your AI fitness mentor!</li>
        </ol>

        <h2>API Documentation</h2>
        <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>

        <h2>Endpoints</h2>
        <ul>
            <li><code>GET /api/v1/fitness/{user_id}/today</code> - Today's data</li>
            <li><code>GET /api/v1/fitness/{user_id}/week</code> - This week's summary</li>
            <li><code>GET /api/v1/fitness/{user_id}/trends</code> - Long-term trends</li>
            <li><code>POST /api/v1/chat</code> - Chat with AI</li>
        </ul>

        <p style="margin-top: 40px; color: #95a5a6;">
            Train like a hero 🏛️
        </p>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "chiron",
        "version": "0.1.0"
    }


# Auth endpoints (stubs for now)
@app.get("/auth/truecoach")
async def auth_truecoach():
    """OAuth flow for TrueCoach."""
    # TODO: Implement OAuth flow
    return {"message": "TrueCoach OAuth not yet implemented"}


@app.get("/auth/truecoach/callback")
async def auth_truecoach_callback(code: str, state: str):
    """OAuth callback for TrueCoach."""
    # TODO: Handle OAuth callback
    return {"message": "TrueCoach connected!", "code": code}


@app.get("/auth/mfp")
async def auth_mfp():
    """Auth flow for MyFitnessPal."""
    # TODO: Implement auth flow
    return {"message": "MyFitnessPal auth not yet implemented"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
