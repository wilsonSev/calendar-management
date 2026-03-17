"""Main entry point for NLP service"""
from datetime import datetime

import yandex_api
from message import Message
from scheduler_client import SchedulerClient


def process_user_message(user_message: str, user_id: str, username: str = "User"):
    """
    Process user message and create event in scheduler

    Args:
        user_message: Raw text from user
        user_id: User ID (e.g., Telegram user ID)
        username: Username for additional context
    """
    add_info = Message(datetime.now(), username)
    parsed_event = yandex_api.parse_message(user_message, add_info)

    print(f"Parsed event: {parsed_event}")

    with SchedulerClient() as client:
        success, event_id = client.create_event(
            title=parsed_event.name,
            description=f"Created by {username}",
            user_id=str(user_id),
            start_time=parsed_event.start_time,
            end_time=parsed_event.finish_time,
            participants=[]
        )

        if success:
            print(f"✓ Event created successfully! ID: {event_id}")
        else:
            print(f"✗ Failed to create event")

        return success, event_id


if __name__ == "__main__":
    print("=== Testing YandexGPT 5 Lite parsing ===\n")

    test_message = "Встреча с командой завтра в 15:00, продлится 2 часа"
    print(f"Input message: {test_message}\n")

    add_info = Message(datetime.now(), "Bogdan")

    print("Sending request to Yandex API...")
    print("(This may take a few seconds)\n")

    try:
        parsed_event = yandex_api.parse_message(test_message, add_info)

        print("\n✓ Parsing successful!")
        print(f"\nParsed Event:")
        print(f"  Name: {parsed_event.name}")
        print(f"  Start: {parsed_event.start_time}")
        print(f"  End: {parsed_event.finish_time}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    # Uncomment below to test full flow with gRPC:
    # process_user_message(test_message, user_id="123456", username="Bogdan")
