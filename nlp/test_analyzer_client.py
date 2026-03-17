"""Test client for Analyzer gRPC service"""
import grpc
from lib.analyzer.v1 import analyzer_pb2, analyzer_pb2_grpc


def test_analyze_text(text: str, user_id: int = 123456):
    """
    Send test request to Analyzer service
    
    Args:
        text: Text to analyze
        user_id: Telegram user ID
    """
    print(f"\n{'='*60}")
    print(f"Testing Analyzer Service")
    print(f"{'='*60}\n")
    
    # Connect to Analyzer service
    channel = grpc.insecure_channel('localhost:50051')
    stub = analyzer_pb2_grpc.AnalyzerServiceStub(channel)
    
    # Create request
    request = analyzer_pb2.AnalyzeTextRequest(
        tg_user_id=user_id,
        text=text,
        timezone="Europe/Moscow",
        chat_id=123
    )
    
    print(f"Sending request:")
    print(f"  User ID: {user_id}")
    print(f"  Text: {text}")
    print(f"  Timezone: Europe/Moscow\n")
    
    try:
        # Send request
        print("→ Calling AnalyzeText...\n")
        response = stub.AnalyzeText(request)
        
        # Check response type
        result_type = response.WhichOneof('result')
        
        print(f"{'='*60}")
        print(f"Response received: {result_type}")
        print(f"{'='*60}\n")
        
        if result_type == 'create_event':
            event = response.create_event
            print("✓ Event created successfully!\n")
            print(f"Event details:")
            print(f"  Title: {event.title}")
            print(f"  Description: {event.description}")
            print(f"  Start: {event.start_time.ToDatetime()}")
            print(f"  End: {event.end_time.ToDatetime()}")
            
        elif result_type == 'need_clarification':
            clarification = response.need_clarification
            print("⚠ Need clarification:\n")
            print(f"  Question: {clarification.question}")
            
        elif result_type == 'error':
            error = response.error
            print("✗ Error occurred:\n")
            print(f"  Message: {error.message}")
        
        else:
            print("? Unknown response type")
        
        print(f"\n{'='*60}\n")
        
    except grpc.RpcError as e:
        print(f"✗ gRPC Error: {e.code()} - {e.details()}\n")
        print("Make sure Analyzer server is running:")
        print("  python analyzer_server.py\n")
    
    finally:
        channel.close()


if __name__ == '__main__':
    # Test cases
    test_cases = [
        "Встреча с командой завтра в 15:00, продлится 2 часа",
        "Созвон в понедельник в 10 утра",
        "Обед сегодня в 13:00",
    ]
    
    print("\n" + "="*60)
    print("Analyzer Service Test Suite")
    print("="*60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n\nTest {i}/{len(test_cases)}")
        test_analyze_text(text, user_id=100000 + i)
        
        if i < len(test_cases):
            input("\nPress Enter to continue to next test...")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")
