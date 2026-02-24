from datetime import datetime
from enum import Enum
import json
import requests

from event import Event
from message import Message
from config import OPENROUTER_API_KEY


class Models(str, Enum):
    """Available LLM models"""
    KatCoder = "z-ai/glm-4.5-air:free"
    Llama = "meta-llama/llama-3.3-70b-instruct:free"
    Stepfun = "stepfun/step-3.5-flash:free"


def parse_message(message: str, add_info: Message) -> Event:
    """
    Parse user message using OpenRouter LLM
    
    Args:
        message: Raw text from user
        add_info: Additional context (timestamp, username)
    
    Returns:
        Event object with parsed data
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Add 'openrouter=your_key' to .env file")

    def get_response_with_event(model_response: dict) -> Event:
        """Extract Event from LLM response"""
        with open("dump.json", "w") as file:
            json.dump(model_response, file, indent=2, ensure_ascii=False)
        
        content = model_response["choices"][0]["message"]["content"]
        
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
    
    print(f"→ Calling OpenRouter API (model: {Models.Llama.value})...")
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": Models.Stepfun,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
            timeout=30  # 30 seconds timeout
        )
        
        print(f"← Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

        print("→ Parsing response...")
        return get_response_with_event(response.json())
        
    except requests.exceptions.Timeout:
        raise Exception("OpenRouter API timeout (30s). Try again later.")
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to OpenRouter API. Check your internet connection.")
    except Exception as e:
        raise Exception(f"OpenRouter API error: {e}")
