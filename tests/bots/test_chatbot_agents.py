from unittest import mock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

from app import models, ports, typings
from app.adapters import agents, stubs
from tests import contracts


class TestStubChatBotAgents(contracts.ChatBotAgentContract):
    def chatbot(self, bot: models.Bot, results: str) -> ports.ChatBotAgent:
        return stubs.ChatBotAgent(bot, results=results)


class TestLangChainChatBotAgents(contracts.ChatBotAgentContract):
    def chatbot(self, bot: models.Bot, results: str) -> ports.ChatBotAgent:
        agent = agents.ChatBotAgent(bot)

        chain = mock.MagicMock(spec=RunnableWithMessageHistory)
        chain.ainvoke.return_value = AIMessage(content=results)
        chain.stream.return_value = [
            AIMessage(content=line) for line in results.splitlines()
        ]

        agent._chain = chain
        return agent


class TestLangChainRAGAgents(contracts.ChatBotAgentContract):
    def chatbot(self, bot: models.Bot, results: str) -> ports.ChatBotAgent:
        vector_store = mock.MagicMock(spec=ports.VectorStore)

        agent = agents.RAGAgent(bot, vector_store=vector_store)

        chain = mock.MagicMock(spec=RunnableWithMessageHistory)
        chain.ainvoke.return_value = {"answer": results}
        chain.stream.return_value = [{"answer": line} for line in results.splitlines()]

        agent._chain = chain
        return agent


@pytest.mark.parametrize(
    "bot__bot_type", [typings.BotType.chatbot, typings.BotType.rag]
)
def test_can_get_agent_from_repo(bot: models.Bot, bot_context_factory) -> None:
    repo = agents.BotAgentRepository()
    contexts = bot_context_factory.create_batch(2)
    bot.contexts = contexts

    agent = repo.get_agent(bot, vector_store=mock.MagicMock(spec=ports.VectorStore))
    assert isinstance(agent, ports.ChatBotAgent)


def test_can_get_agent_from_stubs(bot: models.Bot) -> None:
    stub_agent = stubs.ChatBotAgent(bot, results="test")
    repo = stubs.BotAgentRepository(stub_agent)

    agent = repo.get_agent(bot, vector_store=mock.MagicMock(spec=ports.VectorStore))
    assert agent == stub_agent
