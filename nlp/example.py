"""Example usage of the NLP service with Scheduler gRPC client"""
from datetime import datetime, timedelta
from scheduler_client import SchedulerClient


def example_create_event():
    """Example: Create an event using the Scheduler client"""
    print("=== Example: Creating an event ===\n")
    
    with SchedulerClient() as client:
        success, event_id = client.create_event(
            title="Team Meeting",
            description="Weekly sync with the development team",
            user_id="user_12345",
            start_time=datetime.now() + timedelta(days=1, hours=10),  # Tomorrow at 10:00
            end_time=datetime.now() + timedelta(days=1, hours=11),    # Tomorrow at 11:00
            participants=["alice@example.com", "bob@example.com"]
        )
        
        if success:
            print(f"✓ Event created successfully!")
            print(f"  Event ID: {event_id}")
        else:
            print("✗ Failed to create event")


def example_create_task():
    """Example: Create a task using the Scheduler client"""
    print("\n=== Example: Creating a task ===\n")
    
    with SchedulerClient() as client:
        success, task_id = client.create_task(
            title="Review pull request",
            description="Review PR #123 for the new feature",
            user_id="user_12345"
        )
        
        if success:
            print(f"✓ Task created successfully!")
            print(f"  Task ID: {task_id}")
        else:
            print("✗ Failed to create task")


def example_manual_connection():
    """Example: Manual connection management"""
    print("\n=== Example: Manual connection ===\n")
    
    client = SchedulerClient()
    
    try:
        client.connect()
        
        # Create multiple events with the same connection
        for i in range(3):
            success, event_id = client.create_event(
                title=f"Event {i+1}",
                description=f"Test event number {i+1}",
                user_id="user_12345",
                start_time=datetime.now() + timedelta(hours=i+1),
                end_time=datetime.now() + timedelta(hours=i+2)
            )
            print(f"Event {i+1}: {'✓' if success else '✗'} {event_id}")
    
    finally:
        client.close()


if __name__ == "__main__":
    print("Scheduler gRPC Client Examples")
    print("=" * 50)
    print("\nMake sure the Scheduler service is running!")
    print("Check SCHEDULER_HOST and SCHEDULER_PORT in .env\n")
    
    try:
        example_create_event()
        example_create_task()
        example_manual_connection()
        
        print("\n" + "=" * 50)
        print("✓ All examples completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is the Scheduler service running?")
        print("2. Check SCHEDULER_HOST and SCHEDULER_PORT in .env")
        print("3. Verify network connectivity")
