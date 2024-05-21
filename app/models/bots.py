import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import Mapped, mapped_column

from app import typings
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
    context: Mapped[list["BotContext"]] = orm.relationship(back_populates="bot")
    data_source: Mapped[str | None] = mapped_column(sa.String(100))


class BotContext(BaseModel):
    """
    Model to store information about bots context
    """

    __tablename__ = "bot_contexts"

    role: Mapped[typings.BotContextRole] = mapped_column(
        sa.Enum(typings.BotContextRole, native_enum=False, length=36), index=True
    )
    content: Mapped[str] = mapped_column(sa.String(1000))

    bot_id = mapped_column(sa.ForeignKey("bots.id"))
    bot: Mapped[Bot] = orm.relationship(back_populates="context")
