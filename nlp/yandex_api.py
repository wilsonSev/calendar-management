from datetime import datetime
from enum import Enum
import json
from openai import OpenAI, APITimeoutError, APIConnectionError, APIStatusError

from event import Event
from message import Message
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID


class Models(str, Enum):
    Lite = "yandexgpt-lite"
    Pro = "yandexgpt"


_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=YANDEX_API_KEY,
            base_url="https://ai.api.cloud.yandex.net/v1",
        )
    return _client


def _model_uri(model: Models) -> str:
    """Build Yandex model URI: gpt://<folder_id>/<model>"""
    return f"gpt://{YANDEX_FOLDER_ID}/{model.value}"


def parse_message(message: str, add_info: Message) -> Event:
    """
    Parse user message using YandexGPT 5 Lite

    Args:
        message: Raw text from user
        add_info: Additional context (timestamp, username)

    Returns:
        Event object with parsed data
    """
    if not YANDEX_API_KEY:
        raise RuntimeError("YANDEX_API_KEY is not set. Add 'YANDEX_API_KEY=your_key' to .env file")
    if not YANDEX_FOLDER_ID:
        raise RuntimeError("YANDEX_FOLDER_ID is not set. Add 'YANDEX_FOLDER_ID=your_folder_id' to .env file")

    def get_response_with_event(content: str) -> Event:
        with open("dump.json", "w") as file:
            json.dump({"content": content}, file, indent=2, ensure_ascii=False)

        # Strip markdown code blocks (with or without language tag)
        import re
        content = re.sub(r"```[a-z]*\n?", "", content).replace("```", "").strip()

        try:
            event_data = json.loads(content)
            start_str = event_data.get("start-time")
            end_str = event_data.get("end-time")

            start_time = datetime.fromisoformat(start_str) if start_str else datetime.now()
            # end-time may be null or missing
            finish_time = datetime.fromisoformat(end_str) if end_str and end_str != "null" else start_time

            return Event(
                name=event_data.get("event-name", "Untitled Event"),
                start_time=start_time,
                finish_time=finish_time
            )
        except Exception as e:
            print(f"Failed to parse JSON: {content}")
            raise e

    from datetime import date
    today = date.today().isoformat()

    prompt = f"""
Сегодня: {today}

Распарсь этот текст в следующий JSON формат:

{{
  "event-name": string,
  "start-time": string (ISO 8601 datetime, например "2026-03-18T14:00:00"),
  "end-time": string (ISO 8601 datetime) или null если не указано
}}

Текст:
{message}

Верни только JSON без пояснений. Все даты должны быть в формате ISO 8601. Не выдумывай информацию, которой нет в тексте.
"""

    model_uri = _model_uri(Models.Lite)
    print(f"→ Calling Yandex API (model: {model_uri})...")

    try:
        response = _get_client().chat.completions.create(
            model=model_uri,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts event information from text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            timeout=30,
        )

        print("← Response received")

        content = response.choices[0].message.content
        print("→ Parsing response...")
        return get_response_with_event(content)

    except APITimeoutError:
        raise Exception("Yandex API timeout (30s). Try again later.")
    except APIConnectionError:
        raise Exception("Cannot connect to Yandex API. Check your internet connection.")
    except APIStatusError as e:
        raise Exception(f"Yandex API error: {e.status_code} - {e.message}")
    except Exception as e:
        raise Exception(f"Yandex API error: {e}")
