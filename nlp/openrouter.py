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
    Llama = "meta-llama/llama-3.2-3b-instruct:free"
    Stepfun = "stepfun/step-3.5-flash:free"
    Qwen = "qwen/qwen3-next-80b-a3b-instruct:free"
    Gemma = "google/gemma-3-4b-it:free"
    Zai = "z-ai/glm-4.5-air:free"
    GPTOSS = "openai/gpt-oss-20b:free"
    Acree = "arcee-ai/trinity-mini:free"


def parse_message(message: str, add_info: Message) -> Event:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set. Add 'openrouter=your_key' to .env file")

    def get_response_with_event(model_response: dict) -> Event:
        with open("dump.json", "w") as file:
            json.dump(model_response, file)
        
        content = model_response["choices"][0]["message"]["content"]
        
        # Simple cleanup if the model creates markdown code block
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        
        try:
            event_data = json.loads(content)
            # Handle potentially missing times gracefully or ensure prompt enforces it
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
  "start-time": date,
  "end-time": date,
}}

Текст:
{message}

Верни только JSON без пояснений, не выдумывай информацию, которой нет в этом сообщении. Если что-то явно не написано здесь, то пропускай это поле.
"""
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": Models.Acree,
            "messages": [
                {
                    "role": "user",
                    "content": f"{{user_message: {prompt}, add_info: {add_info}}}",
                }
            ],
        },
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.text}")

    print("Response from OpenRouter:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return get_response_with_event(response.json())
