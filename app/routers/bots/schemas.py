import pydantic

from app import typings
from app.routers import common_schemas as common


class BotContextCreate(common.BaseInputSchema):
    """
    Schema for creating bot context
    """

    role: typings.BotContextRole
    content: str = pydantic.Field(max_length=1000)


class BotCreate(common.BaseInputSchema):
    """
    Schema for creating new Bot
    """

    name: str = pydantic.Field(max_length=100)
    avatar: str = pydantic.Field("1f916", max_length=36)
    welcome_message: str | None = pydantic.Field(None, max_length=255)
    contexts: list[BotContextCreate] = pydantic.Field(default_factory=list)
    data_source: str | None = pydantic.Field(None, max_length=100)


class BotContextOutput(common.BaseModelOutput, BotContextCreate):
    """
    Schema for returning bot context
    """


class BotOutput(common.BaseModelOutput):
    """
    Schema for returning bot
    """

    name: str
    avatar: str
    welcome_message: str | None = None
    data_source: typings.BotDataSource | None = None
    contexts: list[BotContextOutput] = pydantic.Field(default_factory=list)
    data_indexed: bool | None = None
    bot_type: typings.BotType = typings.BotType.chatbot
    bot_model: typings.BotModelTypes = typings.BotModelTypes.gpt_4o
    temperature: int
    top_p: int
    max_tokens: int


class ChatMessage(common.BaseInputSchema):
    """
    Schema for chat message
    """

    message: str = pydantic.Field(max_length=1000)
    session_id: str


class ChatOutput(common.BaseOutputSchema):
    """
    Schema for chatbot message ouput
    """

    content: str
