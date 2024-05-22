import abc
import uuid

import pytest

from app import models, ports


class ChatBotAgentContract(abc.ABC):

    @abc.abstractmethod
    def chatbot(self, results: str) -> ports.ChatBotAgent:
        raise NotImplementedError()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message,response", [("Hello bot", "Hi, user")])
    async def test_can_invoke(
        self, bot: models.Bot, message: str, response: str
    ) -> None:
        session_id = str(uuid.uuid4())
        agent = self.chatbot(response)
        agent.initialize(bot)

        result = await agent.invoke(session_id, message)
        assert result == response

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message,response", [("Hello bot", "This is a string\nwith multiple lines\n")]
    )
    async def test_can_stream(
        self, bot: models.Bot, message: str, response: str
    ) -> None:
        session_id = str(uuid.uuid4())
        agent = self.chatbot(response)
        agent.initialize(bot)

        chunks = response.splitlines()

        for idx, result in enumerate(agent.stream(session_id, message)):
            assert result == chunks[idx]
