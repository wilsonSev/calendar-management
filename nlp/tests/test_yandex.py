"""Tests for yandex_api.parse_message function"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from yandex_api import parse_message
from event import Event
from message import Message


ADD_INFO = Message(sent=datetime(2026, 3, 17, 12, 0), user="test_user")


def make_completion(content: str) -> MagicMock:
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


class TestParseMessageSuccess:

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_basic_event(self, mock_get_client):
        mock_get_client.return_value.chat.completions.create.return_value = make_completion(
            '{"event-name": "Встреча", "start-time": "2026-03-18T15:00:00", "end-time": "2026-03-18T17:00:00"}'
        )

        result = parse_message("Встреча завтра в 15:00", ADD_INFO)

        assert isinstance(result, Event)
        assert result.name == "Встреча"
        assert result.start_time == datetime(2026, 3, 18, 15, 0)
        assert result.finish_time == datetime(2026, 3, 18, 17, 0)

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_strips_markdown_code_block(self, mock_get_client):
        mock_get_client.return_value.chat.completions.create.return_value = make_completion(
            '```json\n{"event-name": "Обед", "start-time": "2026-03-17T13:00:00", "end-time": "2026-03-17T14:00:00"}\n```'
        )

        result = parse_message("Обед сегодня в 13:00", ADD_INFO)

        assert result.name == "Обед"
        assert result.start_time == datetime(2026, 3, 17, 13, 0)

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_missing_end_time_falls_back_to_start(self, mock_get_client):
        mock_get_client.return_value.chat.completions.create.return_value = make_completion(
            '{"event-name": "Звонок", "start-time": "2026-03-18T10:00:00"}'
        )

        result = parse_message("Звонок завтра в 10:00", ADD_INFO)

        assert result.finish_time == result.start_time

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_missing_event_name_uses_default(self, mock_get_client):
        mock_get_client.return_value.chat.completions.create.return_value = make_completion(
            '{"start-time": "2026-03-18T09:00:00", "end-time": "2026-03-18T10:00:00"}'
        )

        result = parse_message("Что-то завтра утром", ADD_INFO)

        assert result.name == "Untitled Event"

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_correct_model_uri(self, mock_get_client):
        mock_create = mock_get_client.return_value.chat.completions.create
        mock_create.return_value = make_completion(
            '{"event-name": "Test", "start-time": "2026-03-18T10:00:00"}'
        )

        parse_message("Test event", ADD_INFO)

        call_kwargs = mock_create.call_args.kwargs
        assert "gpt://fake-folder/yandexgpt-lite" == call_kwargs["model"]
        assert call_kwargs["temperature"] == 0.2


class TestParseMessageErrors:

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_invalid_json_raises(self, mock_get_client):
        mock_get_client.return_value.chat.completions.create.return_value = make_completion(
            "это не json"
        )

        with pytest.raises(Exception):
            parse_message("Встреча", ADD_INFO)

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_timeout_raises(self, mock_get_client):
        from openai import APITimeoutError
        mock_get_client.return_value.chat.completions.create.side_effect = APITimeoutError(
            request=MagicMock()
        )

        with pytest.raises(Exception, match="timeout"):
            parse_message("Встреча", ADD_INFO)

    @patch("yandex_api._get_client")
    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", "fake-folder")
    def test_connection_error_raises(self, mock_get_client):
        from openai import APIConnectionError
        mock_get_client.return_value.chat.completions.create.side_effect = APIConnectionError(
            request=MagicMock()
        )

        with pytest.raises(Exception, match="connect"):
            parse_message("Встреча", ADD_INFO)

    @patch("yandex_api.YANDEX_API_KEY", None)
    def test_missing_api_key_raises(self):
        with pytest.raises(RuntimeError, match="YANDEX_API_KEY"):
            parse_message("Встреча", ADD_INFO)

    @patch("yandex_api.YANDEX_API_KEY", "fake-key")
    @patch("yandex_api.YANDEX_FOLDER_ID", None)
    def test_missing_folder_id_raises(self):
        with pytest.raises(RuntimeError, match="YANDEX_FOLDER_ID"):
            parse_message("Встреча", ADD_INFO)
