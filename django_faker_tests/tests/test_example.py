from faker import Faker
from django import test
from django_faker import DjangoFaker
from django_faker.populator import Populator
from ..models import Assessment, Question, Answer, AnswerSubmission, Company, Game, Player, Action

fake = Faker()


class PopulatorTestCase(test.TestCase):

    def testPopulation(self):
        generator = fake
        populator = Populator(generator)
        populator.add_entity(Game, 10)
        self.assertEqual(len(populator.execute()[Game]), 10)

    def testGuesser(self):
        generator = fake

        def title_fake(arg):
            title_fake.count += 1
            name = generator.company()
            return name

        title_fake.count = 0

        populator = Populator(generator)
        populator.add_entity(Game, 10, {
            'title': title_fake
        })
        self.assertEqual(len(populator.execute()[Game]), title_fake.count)

    def testFormatter(self):
        generator = fake

        populator = Populator(generator)

        populator.add_entity(Game, 5)
        populator.add_entity(Player, 10, {
            'score': lambda x: fake.random_int(0, 1000),
            'nickname': lambda x: fake.email()
        })
        populator.add_entity(Action, 30)

        insertedPks = populator.execute()

        self.assertTrue(len(insertedPks[Game]) == 5)
        self.assertTrue(len(insertedPks[Player]) == 10)

        self.assertTrue(any([0 <= p.score <= 1000 and '@' in p.nickname for p in Player.objects.all()]))


class ExampleTestCase(test.TestCase):

    def setUp(self):
        # populator gets shared, need to reset it
        populator = DjangoFaker.get_populator()
        populator.clear()

    def test_complex(self):
        """Should be able to populate a complex set of models"""
        populator = DjangoFaker.get_populator()
        populator.add_entity(Assessment, 5)
        populator.add_entity(Question, 5)
        populator.add_entity(AnswerSubmission, 5)
        populator.add_entity(Company, 5)
        populator.add_entity(Answer, 5)
        results = populator.execute()
        self.assertEqual(len(results[Assessment]), 5)
        self.assertEqual(len(results[Question]), 5)
        self.assertEqual(len(results[AnswerSubmission]), 5)
        self.assertEqual(len(results[Company]), 5)
        self.assertEqual(len(results[Answer]), 5)
