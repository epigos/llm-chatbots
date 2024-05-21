import uuid

import factory

from app import models


class BotFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")
    welcome_message = factory.Faker("sentence")

    class Meta:
        model = models.Bot
