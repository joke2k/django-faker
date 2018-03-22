from faker import Faker
from django_faker import DjangoFaker
from django import test


fake = Faker()


class APIDjangoFakerTestCase(test.TestCase):

    def test_django_faker_singleton(self):
        self.assertEqual(DjangoFaker(), DjangoFaker())
        self.assertIs(DjangoFaker(), DjangoFaker())

    def test_faker_cache_generator(self):
        self.assertEqual(DjangoFaker().get_generator(), DjangoFaker().get_generator())
        self.assertIs(DjangoFaker().get_generator(), DjangoFaker().get_generator())
        self.assertIs(DjangoFaker().get_generator(codename='default'), DjangoFaker().get_generator(codename='default'))

        self.assertEqual(DjangoFaker().get_generator(locale='it_IT'), DjangoFaker().get_generator(locale='it_IT'))
        self.assertIs(DjangoFaker().get_generator(locale='it_IT'), DjangoFaker().get_generator(locale='it_IT'))

    def test_faker_cache_populator(self):
        self.assertEqual(DjangoFaker().get_generator(), DjangoFaker().get_generator())
        self.assertIs(DjangoFaker().get_generator(), DjangoFaker().get_generator())
        self.assertIs(DjangoFaker().get_generator(), DjangoFaker().get_generator())

        self.assertEqual(DjangoFaker().get_generator(locale='it_IT'), DjangoFaker().get_generator(locale='it_IT'))
        self.assertIs(DjangoFaker().get_generator(locale='it_IT'), DjangoFaker().get_generator(locale='it_IT'))
