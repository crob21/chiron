"""Google Gemini AI service."""
import google.generativeai as genai
from typing import Dict, List, Optional
import logging
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GeminiService:
    """Service for Google Gemini AI integration."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        genai.configure(api_key=self.api_key)

        # Define fitness data functions
        self.fitness_tools = self._create_fitness_tools()

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            tools=[self.fitness_tools]
        )

    def _create_fitness_tools(self):
        """Create function declarations for Gemini."""
        get_today_function = genai.protos.FunctionDeclaration(
            name="get_todays_fitness",
            description="Get today's workout and nutrition data for the user",
            parameters={
                "type": "object",
                "properties": {}
            }
        )

        get_week_function = genai.protos.FunctionDeclaration(
            name="get_weekly_fitness",
            description="Get this week's workout and nutrition summary",
            parameters={
                "type": "object",
                "properties": {}
            }
        )

        get_trends_function = genai.protos.FunctionDeclaration(
            name="get_fitness_trends",
            description="Get fitness trends over a period of time",
            parameters={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze (default 30)"
                    }
                }
            }
        )

        return genai.protos.Tool(
            function_declarations=[
                get_today_function,
                get_week_function,
                get_trends_function
            ]
        )

    async def analyze_fitness_data(self, data: Dict) -> str:
        """
        Analyze fitness data and provide insights.

        Args:
            data: Fitness data dictionary with workouts and nutrition

        Returns:
            AI-generated analysis and insights
        """
        prompt = f"""
        Analyze this fitness data and provide personalized insights:

        Workouts: {data.get('workouts', [])}
        Nutrition: {data.get('nutrition', {})}

        Provide insights on:
        1. Recovery needs based on workout intensity
        2. Calorie adequacy for the training load
        3. Macro balance for performance goals
        4. Suggestions for tomorrow

        Be specific, actionable, and encouraging.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return "Unable to generate insights at this time."

    async def chat(
        self,
        message: str,
        context: Optional[Dict] = None,
        chat_history: Optional[List] = None
    ) -> str:
        """
        Chat with AI about fitness.

        Args:
            message: User's message/question
            context: Current fitness data context
            chat_history: Previous chat messages

        Returns:
            AI response
        """
        # Build context prompt
        context_str = ""
        if context:
            context_str = f"""
            Current Context:
            - Recent workouts: {context.get('workouts', 'None')}
            - Nutrition today: {context.get('nutrition', 'None')}
            - Goals: {context.get('goals', 'Not set')}
            """

        full_prompt = f"{context_str}\n\nUser: {message}"

        try:
            # Start or continue chat
            if chat_history:
                chat = self.model.start_chat(history=chat_history)
            else:
                chat = self.model.start_chat()

            response = chat.send_message(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat failed: {e}")
            return "I'm having trouble responding right now. Please try again."

    def create_workout_summary(self, workouts: List[Dict]) -> str:
        """Generate a natural language workout summary."""
        if not workouts:
            return "No workouts recorded."

        prompt = f"""
        Summarize these workouts in 2-3 sentences:
        {workouts}

        Be concise and highlight key achievements or patterns.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Workout summary failed: {e}")
            return "Unable to summarize workouts."
