"""Chiron Python client for easy integration with Gemini."""
import aiohttp
import google.generativeai as genai
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ChironChat:
    """
    Chiron client for chatting with AI about your fitness data.

    This client connects to your Chiron API and uses Gemini to provide
    intelligent fitness insights based on your actual workout and nutrition data.

    Usage:
        chat = ChironChat(user_id="your_id", api_key="your_key")
        response = await chat.send_message("How am I doing today?")
        print(response)
    """

    def __init__(
        self,
        user_id: str,
        api_key: str,
        chiron_api_base: str = "http://localhost:8000/api/v1",
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize Chiron chat client.

        Args:
            user_id: Your Chiron user ID
            api_key: Your Chiron API key
            chiron_api_base: Base URL for Chiron API
            gemini_api_key: Google Gemini API key (optional if set in env)
        """
        self.user_id = user_id
        self.api_key = api_key
        self.api_base = chiron_api_base

        # Configure Gemini
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)

        # Define functions for Gemini to call
        self.fitness_tools = self._create_fitness_tools()

        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            tools=[self.fitness_tools]
        )

        # Start chat
        self.chat = self.model.start_chat()

    def _create_fitness_tools(self):
        """Create function declarations for Gemini."""
        get_today_function = genai.protos.FunctionDeclaration(
            name="get_todays_fitness",
            description="Get today's workout and nutrition data",
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
            description="Get fitness trends over time",
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

    async def send_message(self, message: str) -> str:
        """
        Send a message to your AI fitness coach.

        Gemini will automatically call your Chiron API to fetch relevant
        data and provide personalized insights.

        Args:
            message: Your question or message

        Returns:
            AI response
        """
        try:
            response = self.chat.send_message(message)

            # Handle function calls
            for part in response.parts:
                if fn := part.function_call:
                    # Gemini wants to call our API!
                    result = await self._handle_function_call(fn)

                    # Send data back to Gemini
                    response = self.chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fn.name,
                                    response={"result": result}
                                )
                            )]
                        )
                    )

            return response.text

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def _handle_function_call(self, fn) -> Dict:
        """Execute function call against Chiron API."""
        url_map = {
            "get_todays_fitness": f"{self.api_base}/fitness/{self.user_id}/today",
            "get_weekly_fitness": f"{self.api_base}/fitness/{self.user_id}/week",
            "get_fitness_trends": f"{self.api_base}/fitness/{self.user_id}/trends"
        }

        url = url_map.get(fn.name)
        if not url:
            return {"error": "Unknown function"}

        # Add days parameter if specified
        params = {"api_key": self.api_key}
        if fn.name == "get_fitness_trends" and hasattr(fn, 'args') and 'days' in fn.args:
            params['days'] = fn.args['days']

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": f"API call failed: {resp.status}"}

    def reset_chat(self):
        """Start a new chat session."""
        self.chat = self.model.start_chat()


# Simple synchronous wrapper for ease of use
class ChironChatSync:
    """Synchronous version of ChironChat."""

    def __init__(self, user_id: str, api_key: str, chiron_api_base: str = "http://localhost:8000/api/v1"):
        import asyncio
        self.loop = asyncio.new_event_loop()
        self.client = ChironChat(user_id, api_key, chiron_api_base)

    def send_message(self, message: str) -> str:
        """Send message synchronously."""
        return self.loop.run_until_complete(self.client.send_message(message))

    def reset_chat(self):
        """Reset chat history."""
        self.client.reset_chat()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def example():
        # Initialize client
        chat = ChironChat(
            user_id="your_user_id",
            api_key="your_api_key",
            chiron_api_base="http://localhost:8000/api/v1"
        )

        # Ask questions - Gemini automatically fetches your data!
        print("User: How am I doing today?")
        response = await chat.send_message("How am I doing today?")
        print(f"Chiron: {response}\n")

        print("User: Should I increase my protein intake?")
        response = await chat.send_message("Should I increase my protein intake?")
        print(f"Chiron: {response}\n")

        print("User: Compare this week to last week")
        response = await chat.send_message("Compare this week to last week")
        print(f"Chiron: {response}\n")

    # Run example
    asyncio.run(example())
