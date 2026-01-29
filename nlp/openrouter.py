from datetime import datetime
from enum import Enum, StrEnum
import json
from dotenv import load_dotenv
import os
from event import Event, dataclass_types_to_json
import requests
from message import Message


class Models(StrEnum):
    KatCoder = "z-ai/glm-4.5-air:free"
    Llama = "meta-llama/llama-3.3-70b-instruct:free"


load_dotenv()

OPENROUTER_API_KEY = os.getenv("openrouter")


def parse_message(message: str, add_info: Message) -> Event:

    def get_response_with_event(model_response: dict) -> Event:
        with open("dump.json", "w") as file:
            json.dump(model_response, file)
        return model_response["choices"][0]["message"]["content"]

    prompt = f"""
  Распарсь этот текст в следующий JSON формат:

      {{
        "event-name": string,
        "start-time": date,
        "end-time": date,
      }}
   
  Текст:
  {message}

  Верни только JSON без пояснений, не выдумывай информацию, которой нет в этом сообщении. Если что-то явно не написано здесь, то пропускай это поле. У участников должны быть имена
  """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": f"{Models.Llama}",
            "messages": [
                {
                    "role": "user",
                    "content": f"{{user_message: {prompt}, add_info: {add_info}}}",
                }
            ],
        },
    )

    return get_response_with_event(response.json())
