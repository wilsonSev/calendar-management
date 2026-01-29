from os import getenv
from dotenv import load_dotenv
import event
import openrouter
from message import Message
import datetime


add_info = Message(datetime.datetime.now(), "Bogdan")

print(event.dataclass_types_to_json(event.Event))
print(
    openrouter.parse_message("оуктукшпукгпукшгрпшукрмшгукмшукмш", add_info),
)
