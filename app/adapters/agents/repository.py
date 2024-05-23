import logging
import typing

from app import models, ports, typings

from .chatbot import ChatBotAgent
from .rag import RAGAgent

_bot_mappings = {typings.BotType.chatbot: ChatBotAgent, typings.BotType.rag: RAGAgent}

logger = logging.getLogger(__name__)


class BotAgentRepository(ports.BotAgentRepository):
    """
    A repository for LLM implemented agents
    """

    def get_agent(self, bot: models.Bot, **kwargs: typing.Any) -> ports.ChatBotAgent:
        try:
            agent_cls = _bot_mappings[bot.bot_type]
        except KeyError as exc:
            raise ValueError(f"No agent implemeted for {bot.bot_type}") from exc

        agent = agent_cls(bot, **kwargs)
        logger.info("Loaded Agent %s for bot type %s", agent, bot.bot_type)
        return typing.cast(ports.ChatBotAgent, agent)
