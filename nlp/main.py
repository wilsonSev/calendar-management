from os import getenv
from dotenv import load_dotenv
import event
import openrouter
from message import Message
import datetime


add_info = Message(datetime.datetime.now(), "Bogdan")

print(
    openrouter.parse_message("Сделай встречу на завтра на 6 вечера на 2 часа", add_info)
)
