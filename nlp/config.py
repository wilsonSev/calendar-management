"""Configuration for NLP service"""
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent directory)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# gRPC service endpoints
SCHEDULER_HOST = getenv("SCHEDULER_HOST", "localhost")
SCHEDULER_PORT = getenv("SCHEDULER_PORT", "50052")  # TODO: update with actual port

# OpenRouter API
OPENROUTER_API_KEY = getenv("openrouter")
