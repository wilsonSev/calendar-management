from datetime import datetime
from enum import Enum
import json
from openai import OpenAI, APITimeoutError, APIConnectionError, APIStatusError

from event import Event
from message import Message
from config import DEEPSEEK_API_KEY


class Models(str, Enum):
    Chat = "deepseek-chat"
    Reasoner = "deepseek-reasoner"


_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    return _client


def parse_message(message: str, add_info: Message) -> Event:
    """
    Parse user message using DeepSeek LLM

    Args:
        message: Raw text from user
        add_info: Additional context (timestamp, username)

    Returns:
        Event object with parsed data
    """
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY is not set. Add 'DEEPSEEK_API_KEY=your_key' to .env file")

    def get_response_with_event(content: str) -> Event:
        with open("dump.json", "w") as file:
            json.dump({"content": content}, file, indent=2, ensure_ascii=False)

        # Simple cleanup if the model creates markdown code block
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")

        try:
            event_data = json.loads(content)
            start_str = event_data.get("start-time")
            end_str = event_data.get("end-time")

            start_time = datetime.fromisoformat(start_str) if start_str else datetime.now()
            finish_time = datetime.fromisoformat(end_str) if end_str else start_time

            return Event(
                name=event_data.get("event-name", "Untitled Event"),
                start_time=start_time,
                finish_time=finish_time
            )
        except Exception as e:
            print(f"Failed to parse JSON: {content}")
            raise e

    prompt = f"""
Распарсь этот текст в следующий JSON формат:

{{
  "event-name": string,
  "start-time": date (ISO format),
  "end-time": date (ISO format)
}}

Текст:
{message}

Верни только JSON без пояснений, не выдумывай информацию, которой нет в этом сообщении.
"""

    print(f"→ Calling DeepSeek API (model: {Models.Chat.value})...")

    try:
        response = _get_client().chat.completions.create(
            model=Models.Chat.value,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts event information from text."},
                {"role": "user", "content": prompt},
            ],
            stream=False,
            timeout=30,
        )

        print(f"← Response received")

        content = response.choices[0].message.content
        print("→ Parsing response...")
        return get_response_with_event(content)

    except APITimeoutError:
        raise Exception("DeepSeek API timeout (30s). Try again later.")
    except APIConnectionError:
        raise Exception("Cannot connect to DeepSeek API. Check your internet connection.")
    except APIStatusError as e:
        raise Exception(f"DeepSeek API error: {e.status_code} - {e.message}")
    except Exception as e:
        raise Exception(f"DeepSeek API error: {e}")
