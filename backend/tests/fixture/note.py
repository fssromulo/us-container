# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class NoteFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Note

    title = factory.Faker("paragraph", nb_sentences=1)
    content = factory.Faker("paragraph", nb_sentences=1)
    author = factory.SubFactory("tests.fixture.UserFactory")
