from datetime import datetime
from enum import Enum
import json
from cerebras.cloud.sdk import Cerebras, APITimeoutError, APIConnectionError, APIStatusError

from event import Event
from message import Message
from config import CEREBRAS_API_KEY


class Models(str, Enum):
    Llama70b = "llama-3.3-70b"
    Llama8b = "llama3.1-8b"


_client = None


def _get_client() -> Cerebras:
    global _client
    if _client is None:
        _client = Cerebras(api_key=CEREBRAS_API_KEY)
    return _client


def parse_message(message: str, add_info: Message) -> Event:
    """
    Parse user message using Cerebras LLM

    Args:
        message: Raw text from user
        add_info: Additional context (timestamp, username)

    Returns:
        Event object with parsed data
    """
    if not CEREBRAS_API_KEY:
        raise RuntimeError("CEREBRAS_API_KEY is not set. Add 'CEREBRAS_API_KEY=your_key' to .env file")

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

    print(f"→ Calling Cerebras API (model: {Models.Llama70b.value})...")

    try:
        response = _get_client().chat.completions.create(
            model=Models.Llama70b.value,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts event information from text."},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=1024,
            temperature=0.2,
            top_p=1,
            stream=False,
        )

        print("← Response received")

        content = response.choices[0].message.content
        print("→ Parsing response...")
        return get_response_with_event(content)

    except APITimeoutError:
        raise Exception("Cerebras API timeout. Try again later.")
    except APIConnectionError:
        raise Exception("Cannot connect to Cerebras API. Check your internet connection.")
    except APIStatusError as e:
        raise Exception(f"Cerebras API error: {e.status_code} - {e.message}")
    except Exception as e:
        raise Exception(f"Cerebras API error: {e}")
