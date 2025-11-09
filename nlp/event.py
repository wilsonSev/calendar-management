from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Event:
    name: str
    start_time: datetime
    finish_time: datetime
    participants: List[str]
