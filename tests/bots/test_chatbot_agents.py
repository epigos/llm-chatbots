from unittest import mock

from langchain_core.messages import AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from app import ports
from app.adapters import agents, stubs
from tests import contracts


class TestStubChatBotAgents(contracts.ChatBotAgentContract):
    def chatbot(self, results: str) -> ports.ChatBotAgent:
        return stubs.ChatBotAgent(results=results)


class TestLangChainChatBotAgents(contracts.ChatBotAgentContract):
    def chatbot(self, results: str) -> ports.ChatBotAgent:
        agent = agents.ChatBotAgent()

        agent._model = mock.MagicMock(spec=ChatOpenAI)

        chain = mock.MagicMock(spec=RunnableWithMessageHistory)
        chain.ainvoke.return_value = AIMessage(content=results)
        chain.stream.return_value = [
            AIMessage(content=line) for line in results.splitlines()
        ]

        agent.initialize = mock.MagicMock()
        agent._chain = chain
        agent._bot = mock.MagicMock()
        return agent
