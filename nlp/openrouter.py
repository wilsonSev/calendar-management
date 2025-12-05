from datetime import datetime
import json
from dotenv import load_dotenv
import os
from event import Event
import requests
import json
from message import Message


load_dotenv()

OPENROUTER_API_KEY = os.getenv("openrouter")


# text -> event
# end_time optional
def parse_message(message: str, add_info: Message) -> Event:
    prompt = f"""
  Распарсь этот текст в следующий JSON формат:

  {{
    "event-name": string,
    "start-time": date,
    "end-time": date,
    "participants": string[]
  }}

  Текст:
  {message}

  Верни только JSON без пояснений.
  """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "kwaipilot/kat-coder-pro:free",
            "messages": [
                {
                    "role": "user",
                    "content": f"{{user_message: {prompt}, add_info: {add_info}}}",
                }
            ],
        },
    )

    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    return None


# completion = client.chat.completions.create(
#     model="sonar-pro", messages=[{"role": "user", "content": prompt}]
# )
# data = json.loads(completion.choices[0].message.content)  # type: ignore

# return Event(
#     name=data.get("event-name"),
#     start_time=datetime.fromisoformat(data.get("start-time")),
#     finish_time=datetime.fromisoformat(data.get("end-time")),
#     participants=data.get("participants", []),
# )
