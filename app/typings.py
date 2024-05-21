import enum


class BotContextRole(str, enum.Enum):
    """Enum for bot context roles."""

    system = "system"
    user = "user"
    assistant = "assistant"
