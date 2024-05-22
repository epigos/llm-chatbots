import collections
import typing

from app import models, ports


class ChatBotAgent(ports.ChatBotAgent):
    """
    Stub implementation of ChatBotAgent for use in testing
    """

    def __init__(self, results: str) -> None:
        self._bot: models.Bot | None = None
        self._results = results
        self._history: dict[tuple[str, str], list[str]] = collections.defaultdict(list)

    def initialize(self, bot: models.Bot) -> None:
        self._bot = bot

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
