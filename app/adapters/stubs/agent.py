import collections
import typing

from app import models, ports


class ChatBotAgent(ports.ChatBotAgent):
    """
    Stub implementation of ChatBotAgent for use in testing
    """

    def __init__(self, bot: models.Bot, results: str) -> None:
        super().__init__(bot)
        self._results = results
        self._history: dict[tuple[str, str], list[str]] = collections.defaultdict(list)

    def initialize(
        self,
    ) -> None:
        pass

    async def invoke(self, session_id: str, message: str) -> str:
        if not self._bot:
            raise RuntimeError("Agent is not initialized")

        self._history[(str(self._bot.id), session_id)].append(message)
        return self._results

    def stream(self, session_id: str, message: str) -> typing.Iterator[str]:
        if not self._bot:
            raise RuntimeError("Agent is not initialized")

        self._history[(str(self._bot.id), session_id)].append(message)
        yield from self._results.splitlines()


class BotAgentRepository(ports.BotAgentRepository):
    """
    Stub implementation of BotAgentRepository for use in testing.
    """

    def __init__(self, agent: ports.ChatBotAgent | None = None) -> None:
        self._agent = agent

    def get_agent(self, bot: models.Bot, **kwargs: typing.Any) -> ports.ChatBotAgent:
        return self._agent or ChatBotAgent(bot, results="test")
