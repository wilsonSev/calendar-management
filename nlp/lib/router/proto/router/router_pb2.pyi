from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DateRange(_message.Message):
    __slots__ = ("start_date", "end_date")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    def __init__(self, start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DateTimeRange(_message.Message):
    __slots__ = ("start_datetime", "end_datetime")
    START_DATETIME_FIELD_NUMBER: _ClassVar[int]
    END_DATETIME_FIELD_NUMBER: _ClassVar[int]
    start_datetime: _timestamp_pb2.Timestamp
    end_datetime: _timestamp_pb2.Timestamp
    def __init__(self, start_datetime: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_datetime: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateEventRequest(_message.Message):
    __slots__ = ("title", "description", "participants", "date", "datetime", "user_id")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DATETIME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    participants: _containers.RepeatedScalarFieldContainer[str]
    date: DateRange
    datetime: DateTimeRange
    user_id: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., participants: _Optional[_Iterable[str]] = ..., date: _Optional[_Union[DateRange, _Mapping]] = ..., datetime: _Optional[_Union[DateTimeRange, _Mapping]] = ..., user_id: _Optional[str] = ...) -> None: ...

class CreateEventResponse(_message.Message):
    __slots__ = ("success", "id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    id: str
    def __init__(self, success: bool = ..., id: _Optional[str] = ...) -> None: ...

class CreateTaskRequest(_message.Message):
    __slots__ = ("title", "description", "user_id")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    user_id: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class CreateTaskResponse(_message.Message):
    __slots__ = ("success", "id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    id: str
    def __init__(self, success: bool = ..., id: _Optional[str] = ...) -> None: ...
