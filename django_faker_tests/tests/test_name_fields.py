from django import test
from django_faker import DjangoFaker
from ..models import NamedFields


class RelationalTestCse(test.TestCase):

    def setUp(self):
        populator = DjangoFaker.get_populator()
        populator.clear()

    def test_all_names(self):
        """"""
        populator = DjangoFaker.get_populator()
        populator.add_entity(NamedFields, 1)
        populator.execute()
        named = NamedFields.objects.all()[0]
        self.assertRegexpMatches(named.is_boolean, '(True)|(False)')
        self.assertRegexpMatches(named.created_at, '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        self.assertRegexpMatches(named.first_name, '[A-Z][a-z]+?')
        self.assertRegexpMatches(named.last_name, '[A-Z][a-z]+?')
        self.assertRegexpMatches(named.name, '\w')
        self.assertRegexpMatches(named.login, '\w')
        self.assertRegexpMatches(named.email, '.+@.*\..*')
        self.assertRegexpMatches(named.phone_number, '[\d\-x]+')
        self.assertRegexpMatches(named.city, '([A-Z][a-z]+? ?)+')
        self.assertRegexpMatches(named.zipcode, '\d+')
        self.assertRegexpMatches(named.state, '[A-Z\']{2}')
        self.assertRegexpMatches(named.country, '([A-Z][a-z]+? ?)+')
        self.assertRegexpMatches(named.title, '[\w ]+.')

