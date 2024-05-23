import enum


class BotModelTypes(str, enum.Enum):
    """Enum for bot types."""

    gpt_4o = "gpt_4o"
    gpt_4_turbo = "gpt_4_turbo"


class BotType(str, enum.Enum):
    """Enum for bot types."""

    chatbot = "chatbot"
    rag = "rag"


class BotDataSource(str, enum.Enum):
    """Enum for bot data source."""

    text = "text"
    uploads = "uploads"
    web = "web"


class BotContextRole(str, enum.Enum):
    """Enum for bot context roles."""

    system = "system"
    user = "user"
    assistant = "assistant"
