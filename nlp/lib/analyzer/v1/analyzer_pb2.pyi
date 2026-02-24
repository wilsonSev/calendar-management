from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzeTextRequest(_message.Message):
    __slots__ = ("tg_user_id", "text", "timezone", "chat_id")
    TG_USER_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    CHAT_ID_FIELD_NUMBER: _ClassVar[int]
    tg_user_id: int
    text: str
    timezone: str
    chat_id: int
    def __init__(self, tg_user_id: _Optional[int] = ..., text: _Optional[str] = ..., timezone: _Optional[str] = ..., chat_id: _Optional[int] = ...) -> None: ...

class AnalyzeTextResponse(_message.Message):
    __slots__ = ("create_event", "need_clarification", "error")
    CREATE_EVENT_FIELD_NUMBER: _ClassVar[int]
    NEED_CLARIFICATION_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    create_event: CreateEvent
    need_clarification: NeedClarification
    error: Error
    def __init__(self, create_event: _Optional[_Union[CreateEvent, _Mapping]] = ..., need_clarification: _Optional[_Union[NeedClarification, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class CreateEvent(_message.Message):
    __slots__ = ("title", "description", "start_time", "end_time")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class NeedClarification(_message.Message):
    __slots__ = ("question",)
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    question: str
    def __init__(self, question: _Optional[str] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
