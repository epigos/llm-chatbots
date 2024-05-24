import uuid

import factory
import factory.fuzzy
from faker import Faker

from app import models, typings

fake = Faker()


class BotContextFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    content = factory.Faker("sentence")
    role = typings.BotContextRole.system

    class Meta:
        model = models.BotContext


class BotDocumentFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    content = factory.Faker("sentence")
    filename = factory.Faker("word")

    class Meta:
        model = models.BotDocument


class BotFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"{fake.word()}-{n}")
    welcome_message = factory.Faker("sentence")
    bot_type = typings.BotType.chatbot
    bot_model = typings.BotModelTypes.gpt_4o
    temperature = factory.fuzzy.FuzzyInteger(low=10, high=100)
    top_p = factory.fuzzy.FuzzyInteger(low=10, high=100)
    max_tokens = factory.fuzzy.FuzzyInteger(low=1000, high=4096)
    contexts = factory.RelatedFactoryList(BotContextFactory)

    class Meta:
        model = models.Bot
