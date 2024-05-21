import uuid

import factory
from faker import Faker

from app import models

fake = Faker()


class BotFactory(factory.Factory):
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"{fake.word()}-{n}")
    welcome_message = factory.Faker("sentence")

    class Meta:
        model = models.Bot
