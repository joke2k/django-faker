from django import test
from django_faker import DjangoFaker
from ..models import Assessment, Question, Answer, AnswerSubmission, Company


class ExampleTestCase(test.TestCase):

    def setUp(self):
        # populator gets shared, need to reset it
        populator = DjangoFaker.get_populator()
        populator.clear()

    def test_complex(self):
        """Should be able to populate a complex database"""
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
