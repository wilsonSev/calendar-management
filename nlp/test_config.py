"""Test configuration loading"""
import os
from config import OPENROUTER_API_KEY, SCHEDULER_HOST, SCHEDULER_PORT

print("=== Configuration Test ===\n")

print(f"Current working directory: {os.getcwd()}")
print(f"Looking for .env in parent directory\n")

print("Loaded configuration:")
print(f"  SCHEDULER_HOST: {SCHEDULER_HOST}")
print(f"  SCHEDULER_PORT: {SCHEDULER_PORT}")
print(f"  OPENROUTER_API_KEY: {OPENROUTER_API_KEY[:20] + '...' if OPENROUTER_API_KEY else 'NOT SET'}")

if not OPENROUTER_API_KEY:
    print("\n✗ ERROR: OPENROUTER_API_KEY is not set!")
    print("\nTroubleshooting:")
    print("1. Check that .env file exists in project root (not in nlp/)")
    print("2. Make sure .env contains: openrouter=your_key_here")
    print("3. No spaces around '=' sign")
    print("4. No quotes around the key")
else:
    print(f"\n✓ API key loaded successfully (length: {len(OPENROUTER_API_KEY)} chars)")
