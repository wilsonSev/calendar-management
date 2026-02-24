"""Quick test for OpenRouter API"""
from datetime import datetime
from message import Message
import openrouter

print("=== OpenRouter API Test ===\n")

# Simple test message
test_message = "Встреча завтра в 14:00"
print(f"Test message: {test_message}\n")

add_info = Message(datetime.now(), "Test User")

try:
    print("Sending request to OpenRouter...")
    print("(This should take 5-15 seconds)\n")
    
    result = openrouter.parse_message(test_message, add_info)
    
    print("\n✓ SUCCESS!")
    print(f"\nParsed event:")
    print(f"  Name: {result.name}")
    print(f"  Start: {result.start_time}")
    print(f"  End: {result.finish_time}")
    print(f"\nResponse saved to: dump.json")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check your OpenRouter API key in .env")
    print("2. Check your internet connection")
    print("3. Try again in a few seconds")
