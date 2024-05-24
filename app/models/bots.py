import typing
import uuid

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app import typings
from app.config import settings
from app.db import BaseModel


class Bot(BaseModel):
    """
    Model to store information bots
    """

    __tablename__ = "bots"

    name: Mapped[str] = mapped_column(sa.String(100), index=True, unique=True)
    avatar: Mapped[str] = mapped_column(
        sa.String(36), default="1f916"
    )  # emoji bot avatar
    welcome_message: Mapped[str | None] = mapped_column(sa.String(255))
    data_source: Mapped[typings.BotDataSource | None] = mapped_column(
        sa.Enum(typings.BotDataSource, native_enum=False, length=36),
        index=True,
        nullable=True,
    )
    bot_type: Mapped[typings.BotType] = mapped_column(
        sa.Enum(typings.BotType, native_enum=False, length=36),
        index=True,
        default=typings.BotType.chatbot,
        server_default=typings.BotType.chatbot.value,
    )
    bot_model: Mapped[typings.BotModelTypes] = mapped_column(
        sa.Enum(typings.BotModelTypes, native_enum=False, length=36),
        default=typings.BotModelTypes.gpt_4o,
        server_default=typings.BotModelTypes.gpt_4o.value,
    )
    temperature: Mapped[int] = mapped_column(default=50, server_default="50")
    top_p: Mapped[int] = mapped_column(default=100, server_default="100")
    max_tokens: Mapped[int] = mapped_column(default=4096, server_default="4096")
    data_indexed: Mapped[bool | None] = mapped_column(
        index=True,
        default=False,
    )

    contexts: Mapped[list["BotContext"]] = orm.relationship(
        back_populates="bot", cascade="all, delete"
    )
    documents: Mapped[list["BotDocument"]] = orm.relationship(
        back_populates="bot", cascade="all, delete", lazy="noload"
    )

    def get_model_name(self) -> str:
        """
        Returns the name of the LLM model to use for this bot.
        """
        return self.bot_model.value.replace("_", "-") or settings.openai_model

    def get_model_params(self) -> dict[str, typing.Any]:
        """
        Returns the configuration for the LLM model.
        """
        return {
            "model_name": self.get_model_name(),
            "temperature": self.temperature / 100,
            "max_tokens": self.max_tokens,
            "model_kwargs": {"top_p": self.top_p / 100},
        }

    def get_context_prompts(self) -> list[tuple[str, str]]:
        """
        Prepare bot context prompts and ensure RAG based bots have the required prompts.
        """
        context_messages = []

        for ctx in self.contexts:
            content = ctx.content
            if self.bot_type == typings.BotType.rag and "{context}" not in content:
                content += "\n{context}"
            context_messages.append((ctx.role.value, content))

        if not context_messages and self.bot_type == typings.BotType.rag:
            context_messages.append((typings.BotContextRole.system.value, "{context}"))

        return context_messages


class BotContext(BaseModel):
    """
    Model to store information about bots context
    """

    __tablename__ = "bot_contexts"

    role: Mapped[typings.BotContextRole] = mapped_column(
        sa.Enum(typings.BotContextRole, native_enum=False, length=36), index=True
    )
    content: Mapped[str] = mapped_column(sa.String(1000))

    bot_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("bots.id"))
    bot: Mapped[Bot] = orm.relationship(back_populates="contexts")


class BotDocument(BaseModel):
    """Model to store bot documents for use with RAG based bots"""

    __tablename__ = "bot_documents"

    content: Mapped[str] = mapped_column(sa.Text())
    doc_metadata: Mapped[dict[str, typing.Any]] = mapped_column(pg.JSONB, default=dict)
    filename: Mapped[str | None]
    content_type: Mapped[str | None]

    bot_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("bots.id"))
    bot: Mapped[Bot] = orm.relationship(back_populates="documents")
