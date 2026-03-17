"""Tests for openrouter.parse_message function"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from openrouter import parse_message
from event import Event
from message import Message


# Helper to build a fake OpenRouter API response
def make_api_response(content: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    mock.text = content
    return mock


ADD_INFO = Message(sent=datetime(2026, 3, 17, 12, 0), user="test_user")


class TestParseMessageSuccess:
    """Happy path tests"""

    @patch("openrouter.requests.post")
    def test_basic_event(self, mock_post):
        """Parses title, start and end time correctly"""
        mock_post.return_value = make_api_response(
            '{"event-name": "Встреча", "start-time": "2026-03-18T15:00:00", "end-time": "2026-03-18T17:00:00"}'
        )

        result = parse_message("Встреча завтра в 15:00", ADD_INFO)

        assert isinstance(result, Event)
        assert result.name == "Встреча"
        assert result.start_time == datetime(2026, 3, 18, 15, 0)
        assert result.finish_time == datetime(2026, 3, 18, 17, 0)

    @patch("openrouter.requests.post")
    def test_strips_markdown_code_block(self, mock_post):
        """Handles LLM wrapping JSON in ```json ... ```"""
        mock_post.return_value = make_api_response(
            '```json\n{"event-name": "Обед", "start-time": "2026-03-17T13:00:00", "end-time": "2026-03-17T14:00:00"}\n```'
        )

        result = parse_message("Обед сегодня в 13:00", ADD_INFO)

        assert result.name == "Обед"
        assert result.start_time == datetime(2026, 3, 17, 13, 0)

    @patch("openrouter.requests.post")
    def test_missing_end_time_falls_back_to_start(self, mock_post):
        """If end-time is absent, finish_time equals start_time"""
        mock_post.return_value = make_api_response(
            '{"event-name": "Звонок", "start-time": "2026-03-18T10:00:00"}'
        )

        result = parse_message("Звонок завтра в 10:00", ADD_INFO)

        assert result.name == "Звонок"
        assert result.finish_time == result.start_time

    @patch("openrouter.requests.post")
    def test_missing_event_name_uses_default(self, mock_post):
        """If event-name is absent, falls back to 'Untitled Event'"""
        mock_post.return_value = make_api_response(
            '{"start-time": "2026-03-18T09:00:00", "end-time": "2026-03-18T10:00:00"}'
        )

        result = parse_message("Что-то завтра утром", ADD_INFO)

        assert result.name == "Untitled Event"

    @patch("openrouter.requests.post")
    def test_correct_api_call_params(self, mock_post):
        """Verifies the request is sent to the right URL with auth header"""
        mock_post.return_value = make_api_response(
            '{"event-name": "Test", "start-time": "2026-03-18T10:00:00"}'
        )

        parse_message("Test event", ADD_INFO)

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args

        assert call_kwargs.kwargs["url"] == "https://openrouter.ai/api/v1/chat/completions"
        assert "Authorization" in call_kwargs.kwargs["headers"]
        assert call_kwargs.kwargs["timeout"] == 30


class TestParseMessageErrors:
    """Error handling tests"""

    @patch("openrouter.requests.post")
    def test_api_error_status_raises(self, mock_post):
        """Non-200 status raises Exception"""
        mock_post.return_value = make_api_response("Unauthorized", status_code=401)

        with pytest.raises(Exception, match="OpenRouter API error"):
            parse_message("Встреча", ADD_INFO)

    @patch("openrouter.requests.post")
    def test_invalid_json_raises(self, mock_post):
        """Malformed JSON from LLM raises Exception"""
        mock_post.return_value = make_api_response("это не json")

        with pytest.raises(Exception):
            parse_message("Встреча", ADD_INFO)

    @patch("openrouter.requests.post")
    def test_timeout_raises(self, mock_post):
        """Timeout raises Exception with readable message"""
        import requests as req
        mock_post.side_effect = req.exceptions.Timeout()

        with pytest.raises(Exception, match="timeout"):
            parse_message("Встреча", ADD_INFO)

    @patch("openrouter.requests.post")
    def test_connection_error_raises(self, mock_post):
        """ConnectionError raises Exception with readable message"""
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError()

        with pytest.raises(Exception, match="connect"):
            parse_message("Встреча", ADD_INFO)

    @patch("openrouter.OPENROUTER_API_KEY", None)
    def test_missing_api_key_raises(self):
        """Missing API key raises RuntimeError before any HTTP call"""
        with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
            parse_message("Встреча", ADD_INFO)
