from datetime import datetime
import json
from perplexity import Perplexity
import os
from event import Event


client = Perplexity()


# text -> event
# end_time optional
def parse_message(message: str) -> Event:
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
    completion = client.chat.completions.create(
        model="sonar-pro", messages=[{"role": "user", "content": prompt}]
    )
    data = json.loads(completion.choices[0].message.content)  # type: ignore

    return Event(
        name=data.get("event-name"),
        start_time=datetime.fromisoformat(data.get("start-time")),
        finish_time=datetime.fromisoformat(data.get("end-time")),
        participants=data.get("participants", []),
    )
