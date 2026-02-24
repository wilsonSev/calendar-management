"""Test script to send requests to mock Scheduler server"""
from datetime import datetime, timedelta
from scheduler_client import SchedulerClient
import time


def test_create_events():
    """Test creating multiple events"""
    print("\n" + "="*70)
    print("Testing Mock Scheduler Server")
    print("="*70 + "\n")
    
    test_events = [
        {
            "title": "Встреча с командой",
            "description": "Обсуждение проекта",
            "user_id": "user_123",
            "start": datetime.now() + timedelta(hours=1),
            "end": datetime.now() + timedelta(hours=2),
        },
        {
            "title": "Созвон с клиентом",
            "description": "Презентация новой функции",
            "user_id": "user_456",
            "start": datetime.now() + timedelta(days=1, hours=10),
            "end": datetime.now() + timedelta(days=1, hours=11),
        },
        {
            "title": "Обед",
            "description": "Перерыв",
            "user_id": "user_789",
            "start": datetime.now() + timedelta(hours=3),
            "end": datetime.now() + timedelta(hours=4),
        },
    ]
    
    with SchedulerClient() as client:
        for i, event_data in enumerate(test_events, 1):
            print(f"\n📤 Sending event {i}/{len(test_events)}: {event_data['title']}")
            
            success, event_id = client.create_event(
                title=event_data['title'],
                description=event_data['description'],
                user_id=event_data['user_id'],
                start_time=event_data['start'],
                end_time=event_data['end'],
                participants=[]
            )
            
            if success:
                print(f"✓ Response: success=True, id={event_id}")
            else:
                print(f"✗ Response: success=False")
            
            # Small delay between requests
            if i < len(test_events):
                time.sleep(0.5)
    
    print("\n" + "="*70)
    print("✓ All events sent!")
    print("="*70 + "\n")


def test_create_tasks():
    """Test creating multiple tasks"""
    print("\n" + "="*70)
    print("Testing Tasks")
    print("="*70 + "\n")
    
    test_tasks = [
        {
            "title": "Написать документацию",
            "description": "API документация для нового сервиса",
            "user_id": "user_123",
        },
        {
            "title": "Code review",
            "description": "Проверить PR #42",
            "user_id": "user_456",
        },
    ]
    
    with SchedulerClient() as client:
        for i, task_data in enumerate(test_tasks, 1):
            print(f"\n📤 Sending task {i}/{len(test_tasks)}: {task_data['title']}")
            
            success, task_id = client.create_task(
                title=task_data['title'],
                description=task_data['description'],
                user_id=task_data['user_id']
            )
            
            if success:
                print(f"✓ Response: success=True, id={task_id}")
            else:
                print(f"✗ Response: success=False")
            
            if i < len(test_tasks):
                time.sleep(0.5)
    
    print("\n" + "="*70)
    print("✓ All tasks sent!")
    print("="*70 + "\n")


def continuous_test():
    """Send requests continuously for stress testing"""
    print("\n" + "="*70)
    print("Continuous Test Mode")
    print("="*70)
    print("\nSending requests every 2 seconds...")
    print("Press Ctrl+C to stop\n")
    
    counter = 1
    
    try:
        with SchedulerClient() as client:
            while True:
                title = f"Test Event #{counter}"
                print(f"📤 Sending: {title}")
                
                success, event_id = client.create_event(
                    title=title,
                    description=f"Automated test event {counter}",
                    user_id=f"test_user_{counter % 10}",
                    start_time=datetime.now() + timedelta(hours=counter),
                    end_time=datetime.now() + timedelta(hours=counter + 1),
                )
                
                if success:
                    print(f"✓ {event_id}\n")
                else:
                    print(f"✗ Failed\n")
                
                counter += 1
                time.sleep(2)
    
    except KeyboardInterrupt:
        print(f"\n\n✓ Sent {counter - 1} requests total\n")


if __name__ == '__main__':
    import sys
    
    print("\n" + "="*70)
    print("Mock Scheduler Test Client")
    print("="*70)
    print("\nMake sure mock_scheduler_server.py is running!")
    print("(Run it in another terminal)\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        continuous_test()
    else:
        try:
            test_create_events()
            test_create_tasks()
            
            print("\n" + "="*70)
            print("✅ All tests completed!")
            print("="*70)
            print("\nCheck the mock server terminal to see received requests.")
            print("\nFor continuous testing, run:")
            print("  python test_mock_scheduler.py --continuous")
            print("="*70 + "\n")
        
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\nMake sure mock_scheduler_server.py is running:")
            print("  python mock_scheduler_server.py\n")
