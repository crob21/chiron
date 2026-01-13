"""Test Chiron integration."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chiron_client import ChironChat


async def test_chat():
    """Test the Chiron chat integration."""
    print("🏛️  Chiron Integration Test\n")

    # Get credentials from environment or prompt
    user_id = os.getenv("CHIRON_USER_ID") or input("Enter your User ID: ")
    api_key = os.getenv("CHIRON_API_KEY") or input("Enter your API Key: ")

    # Initialize client
    print("\n✅ Initializing Chiron client...")
    chat = ChironChat(
        user_id=user_id,
        api_key=api_key,
        chiron_api_base="http://localhost:8000/api/v1"
    )

    # Test questions
    questions = [
        "What's my fitness data for today?",
        "How many workouts did I complete this week?",
        "Should I increase my protein intake based on my recent training?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print(f"{'='*60}")

        try:
            response = await chat.send_message(question)
            print(f"\n🤖 Chiron: {response}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

        if i < len(questions):
            print("\n⏳ Waiting 2 seconds before next question...")
            await asyncio.sleep(2)

    print(f"\n{'='*60}")
    print("✅ Test completed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_chat())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
