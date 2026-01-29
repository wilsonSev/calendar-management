from dataclasses import dataclass, fields
from datetime import datetime
import json
from google.protobuf.timestamp_pb2 import Timestamp


@dataclass
class Event:
    name: str
    start_time: datetime
    finish_time: datetime


def dataclass_types_to_json(cls):
    schema = {}
    for f in fields(cls):  # noqa: F821
        t = f.type
        print(t)
        # if hasattr(t, "__name__"):
        #     type_str = t.__name__  # type: ignore
        # else:
        type_str = str(t).replace("typing.", "")
        schema[f.name] = type_str
    return json.dumps(schema, indent=2, ensure_ascii=False)
