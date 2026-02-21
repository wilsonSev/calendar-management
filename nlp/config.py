"""Configuration for NLP service"""
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# gRPC service endpoints
SCHEDULER_HOST = getenv("SCHEDULER_HOST", "localhost")
SCHEDULER_PORT = getenv("SCHEDULER_PORT", "50052")  # TODO: update with actual port

# OpenRouter API
OPENROUTER_API_KEY = getenv("openrouter")
