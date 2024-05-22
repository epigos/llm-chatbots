from langchain_community.chat_message_histories import RedisChatMessageHistory

from app.config import settings


def get_session_history(bot_id: str, session_id: str) -> RedisChatMessageHistory:
    """
    Get session history
    """
    session_key = f"{bot_id}_{session_id}"
    return RedisChatMessageHistory(session_key, url=settings.redis_url)
