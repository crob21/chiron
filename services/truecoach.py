"""TrueCoach API client."""
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class TrueCoachClient:
    """Client for TrueCoach API integration."""

    BASE_URL = "https://api.truecoach.co/api/v1"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict:
        """Exchange OAuth code for access token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/oauth/token",
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"TrueCoach token exchange failed: {resp.status}")
                    raise Exception(f"Failed to exchange code: {resp.status}")

    async def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh access token."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/oauth/token",
                json={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            ) as resp:
                return await resp.json()

    async def get_workouts(
        self,
        access_token: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Fetch workouts from TrueCoach.

        Args:
            access_token: OAuth access token
            start_date: Start date for workouts (defaults to today)
            end_date: End date for workouts (defaults to today)

        Returns:
            List of workout dictionaries
        """
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = date.today()

        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/workouts",
                headers=headers,
                params=params
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("workouts", [])
                else:
                    logger.error(f"Failed to fetch workouts: {resp.status}")
                    return []

    async def get_workout_detail(self, access_token: str, workout_id: str) -> Optional[Dict]:
        """Get detailed workout information."""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/workouts/{workout_id}",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    def parse_workout(self, workout_data: Dict) -> Dict:
        """
        Parse TrueCoach workout data into our format.

        Args:
            workout_data: Raw workout data from TrueCoach

        Returns:
            Parsed workout dictionary
        """
        return {
            "external_id": workout_data.get("id"),
            "date": workout_data.get("date"),
            "title": workout_data.get("name"),
            "notes": workout_data.get("notes"),
            "coach_notes": workout_data.get("coach_notes"),
            "duration_minutes": workout_data.get("duration"),
            "exercises": workout_data.get("exercises", []),
            "source": "truecoach"
        }
