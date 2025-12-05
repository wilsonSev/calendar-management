from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    sent: datetime
    user: str
