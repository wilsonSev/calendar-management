"""Test script to verify gRPC connection to Scheduler service"""
from datetime import datetime, timedelta
from scheduler_client import SchedulerClient


def test_create_event():
    """Test creating an event"""
    print("Testing Scheduler gRPC connection...")
    
    try:
        with SchedulerClient() as client:
            success, event_id = client.create_event(
                title="Test Event",
                description="This is a test event created from Python",
                user_id="test_user_123",
                start_time=datetime.now() + timedelta(hours=1),
                end_time=datetime.now() + timedelta(hours=2),
                participants=["test@example.com"]
            )
            
            if success:
                print(f"✓ SUCCESS: Event created with ID: {event_id}")
            else:
                print("✗ FAILED: Event creation returned success=False")
                
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print("\nMake sure:")
        print("1. Scheduler service is running")
        print("2. SCHEDULER_HOST and SCHEDULER_PORT are correct in .env")


def test_create_task():
    """Test creating a task"""
    print("\nTesting task creation...")
    
    try:
        with SchedulerClient() as client:
            success, task_id = client.create_task(
                title="Test Task",
                description="This is a test task created from Python",
                user_id="test_user_123"
            )
            
            if success:
                print(f"✓ SUCCESS: Task created with ID: {task_id}")
            else:
                print("✗ FAILED: Task creation returned success=False")
                
    except Exception as e:
        print(f"✗ ERROR: {e}")


if __name__ == "__main__":
    test_create_event()
    test_create_task()
