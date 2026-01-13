"""API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime, timedelta
from database.db import get_db
from models import User, Workout, Nutrition
from services import GeminiService
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/v1")


def verify_api_key(api_key: str, db: Session) -> User:
    """Verify API key and return user."""
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


@router.get("/fitness/{user_id}/today")
async def get_today(
    user_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get today's fitness data."""
    user = verify_api_key(api_key, db)
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    today = date.today()

    # Get today's workouts
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date == today
    ).all()

    # Get today's nutrition
    nutrition = db.query(Nutrition).filter(
        Nutrition.user_id == user_id,
        Nutrition.date == today
    ).first()

    return {
        "date": today.isoformat(),
        "workouts": [
            {
                "id": w.id,
                "title": w.title,
                "duration_minutes": w.duration_minutes,
                "exercises": w.exercises,
                "notes": w.notes,
                "total_volume": w.total_volume
            }
            for w in workouts
        ],
        "nutrition": {
            "calories": nutrition.calories if nutrition else 0,
            "protein": nutrition.protein if nutrition else 0,
            "carbs": nutrition.carbs if nutrition else 0,
            "fat": nutrition.fat if nutrition else 0,
            "fiber": nutrition.fiber if nutrition else 0
        } if nutrition else None
    }


@router.get("/fitness/{user_id}/week")
async def get_week(
    user_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get this week's fitness data."""
    user = verify_api_key(api_key, db)
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Calculate week range (Monday to Sunday)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Get workouts
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date >= start_of_week,
        Workout.date <= end_of_week
    ).order_by(Workout.date).all()

    # Get nutrition
    nutrition_entries = db.query(Nutrition).filter(
        Nutrition.user_id == user_id,
        Nutrition.date >= start_of_week,
        Nutrition.date <= end_of_week
    ).order_by(Nutrition.date).all()

    # Calculate weekly totals
    total_workouts = len(workouts)
    total_volume = sum(w.total_volume or 0 for w in workouts)
    avg_calories = sum(n.calories or 0 for n in nutrition_entries) / len(nutrition_entries) if nutrition_entries else 0

    return {
        "week_start": start_of_week.isoformat(),
        "week_end": end_of_week.isoformat(),
        "summary": {
            "total_workouts": total_workouts,
            "total_volume": total_volume,
            "avg_daily_calories": round(avg_calories, 1)
        },
        "workouts": [
            {
                "date": w.date.isoformat(),
                "title": w.title,
                "duration_minutes": w.duration_minutes,
                "total_volume": w.total_volume
            }
            for w in workouts
        ],
        "nutrition": [
            {
                "date": n.date.isoformat(),
                "calories": n.calories,
                "protein": n.protein,
                "carbs": n.carbs,
                "fat": n.fat
            }
            for n in nutrition_entries
        ]
    }


@router.get("/fitness/{user_id}/trends")
async def get_trends(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get fitness trends over time."""
    user = verify_api_key(api_key, db)
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Get workouts
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date >= start_date,
        Workout.date <= end_date
    ).order_by(Workout.date).all()

    # Get nutrition
    nutrition_entries = db.query(Nutrition).filter(
        Nutrition.user_id == user_id,
        Nutrition.date >= start_date,
        Nutrition.date <= end_date
    ).order_by(Nutrition.date).all()

    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "workout_trend": [
            {
                "date": w.date.isoformat(),
                "volume": w.total_volume,
                "duration": w.duration_minutes
            }
            for w in workouts
        ],
        "nutrition_trend": [
            {
                "date": n.date.isoformat(),
                "calories": n.calories,
                "protein": n.protein
            }
            for n in nutrition_entries
        ]
    }


@router.post("/chat")
async def chat(
    message: str,
    user_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Chat with AI about fitness."""
    user = verify_api_key(api_key, db)
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get recent context (last 7 days)
    today = date.today()
    week_ago = today - timedelta(days=7)

    workouts = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date >= week_ago
    ).all()

    nutrition_entries = db.query(Nutrition).filter(
        Nutrition.user_id == user_id,
        Nutrition.date >= week_ago
    ).all()

    # Build context
    context = {
        "workouts": [
            {
                "date": w.date.isoformat(),
                "title": w.title,
                "exercises": w.exercises
            }
            for w in workouts
        ],
        "nutrition": [
            {
                "date": n.date.isoformat(),
                "calories": n.calories,
                "protein": n.protein
            }
            for n in nutrition_entries
        ]
    }

    # Get AI response
    gemini = GeminiService()
    response = await gemini.chat(message, context)

    return {
        "message": message,
        "response": response,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/user/{user_id}/profile")
async def get_profile(
    user_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get user profile."""
    user = verify_api_key(api_key, db)
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": user.id,
        "email": user.email,
        "connections": {
            "truecoach": user.truecoach_connected,
            "myfitnesspal": user.mfp_connected
        },
        "sync_enabled": user.sync_enabled,
        "last_sync": user.last_sync.isoformat() if user.last_sync else None,
        "created_at": user.created_at.isoformat()
    }
