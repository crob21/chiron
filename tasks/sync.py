"""Background sync tasks."""
import logging
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from database.db import SessionLocal
from models import User, Workout, Nutrition
from services import TrueCoachClient, MyFitnessPalClient
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def sync_user_data(user_id: str, days: int = 7) -> bool:
    """
    Sync fitness data for a specific user.

    Args:
        user_id: User ID to sync
        days: Number of days to sync (default 7)

    Returns:
        True if successful, False otherwise
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.sync_enabled:
            return False

        logger.info(f"Syncing data for user {user.email}")

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Sync TrueCoach workouts
        if user.truecoach_connected and user.truecoach_token:
            try:
                await sync_truecoach_data(db, user, start_date, end_date)
            except Exception as e:
                logger.error(f"TrueCoach sync failed for {user.email}: {e}")

        # Sync MyFitnessPal nutrition
        if user.mfp_connected and user.mfp_token:
            try:
                await sync_mfp_data(db, user, start_date, end_date)
            except Exception as e:
                logger.error(f"MyFitnessPal sync failed for {user.email}: {e}")

        # Update last sync time
        user.last_sync = datetime.utcnow()
        db.commit()

        logger.info(f"Successfully synced data for {user.email}")
        return True

    except Exception as e:
        logger.error(f"User sync failed for {user_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


async def sync_truecoach_data(
    db: Session,
    user: User,
    start_date: date,
    end_date: date
):
    """Sync workouts from TrueCoach."""
    client = TrueCoachClient(
        settings.truecoach_client_id,
        settings.truecoach_client_secret
    )

    # Fetch workouts
    workouts = await client.get_workouts(
        user.truecoach_token,
        start_date,
        end_date
    )

    for workout_data in workouts:
        parsed = client.parse_workout(workout_data)

        # Check if workout already exists
        existing = db.query(Workout).filter(
            Workout.user_id == user.id,
            Workout.external_id == parsed["external_id"]
        ).first()

        if existing:
            # Update existing workout
            for key, value in parsed.items():
                setattr(existing, key, value)
        else:
            # Create new workout
            workout = Workout(
                user_id=user.id,
                **parsed
            )
            db.add(workout)

    db.commit()
    logger.info(f"Synced {len(workouts)} workouts from TrueCoach")


async def sync_mfp_data(
    db: Session,
    user: User,
    start_date: date,
    end_date: date
):
    """Sync nutrition data from MyFitnessPal."""
    client = MyFitnessPalClient(
        settings.mfp_username,
        settings.mfp_password
    )

    # Iterate through each day
    current_date = start_date
    count = 0

    while current_date <= end_date:
        nutrition_data = await client.get_nutrition(current_date)

        if nutrition_data:
            parsed = client.parse_nutrition(nutrition_data)

            # Check if nutrition entry already exists
            existing = db.query(Nutrition).filter(
                Nutrition.user_id == user.id,
                Nutrition.date == current_date
            ).first()

            if existing:
                # Update existing entry
                for key, value in parsed.items():
                    if key != 'date':
                        setattr(existing, key, value)
            else:
                # Create new entry
                nutrition = Nutrition(
                    user_id=user.id,
                    date=current_date,
                    **{k: v for k, v in parsed.items() if k != 'date'}
                )
                db.add(nutrition)

            count += 1

        current_date += timedelta(days=1)

    db.commit()
    logger.info(f"Synced {count} days of nutrition from MyFitnessPal")


async def sync_all_users():
    """Sync data for all active users."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.sync_enabled == True).all()
        logger.info(f"Starting sync for {len(users)} users")

        for user in users:
            try:
                await sync_user_data(user.id)
            except Exception as e:
                logger.error(f"Failed to sync user {user.email}: {e}")

        logger.info("Completed sync for all users")
    finally:
        db.close()
