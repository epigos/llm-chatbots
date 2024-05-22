from unittest.mock import patch

import pytest
from langchain_community.chat_message_histories import RedisChatMessageHistory

from app.adapters.agents import utils
from app.config import settings


@pytest.fixture
def mock_redis_chat_message_history():
    with patch.object(RedisChatMessageHistory, "__init__") as mock_init:
        mock_init.return_value = None
        yield mock_init


def test_get_session_history(mock_redis_chat_message_history):
    """
    Test get_session_history function
    """
    bot_id = "test_bot"
    session_id = "1234"

    session_key = f"{bot_id}_{session_id}"
    expected_url = settings.redis_url

    # Call the function
    history = utils.get_session_history(bot_id, session_id)

    # Assert function calls
    mock_redis_chat_message_history.assert_called_once_with(
        session_key, url=expected_url
    )

    # Assert return type (optional)
    assert isinstance(history, RedisChatMessageHistory)
