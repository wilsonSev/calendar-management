"""Quick test for OpenRouter API"""
from datetime import datetime
from message import Message
import openrouter
import deepseek_api
import corebras
import yandex_api

test_message = "Встреча по попводу академической разности завтра в 14:00 длиной в полтора часа"
print(f"Test message: {test_message}\n")

add_info = Message(datetime.now(), "Test User")

try:
    print("Sending request to OpenRouter...")
    print("(This should take 5-15 seconds)\n")

    result = yandex_api.parse_message(test_message, add_info)
    
    print("\n✓ SUCCESS!")
    print(f"\nParsed event:")
    print(f"  Name: {result.name}")
    print(f"  Start: {result.start_time}")
    print(f"  End: {result.finish_time}")
    print(f"\nResponse saved to: dump.json")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
