from faker import Faker
from django_faker.populator import Populator
from django_faker import DjangoFaker

from django import test
from django.template import Context
from django.template import Template
from ..models import Game, Player, Action

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


class TemplateTagsTestCase(test.TestCase):

    @staticmethod
    def render(template, context=None):
        t = Template("{% load fakers %}" + template)
        c = Context(context or {})
        text = t.render(c)
        return text

    # do_fake: fake
    def testSimpleFakeTag(self):
        self.assertNotEqual(self.render("{% fake 'name' as myname %}{{ myname }}"), "")

    def testSimpleFakeTagWithArguments(self):
        self.assertNotEqual(self.render("{% fake 'date_time_between' '-10d' as mydate %}{{ mydate }}"), "")

    def testSimpleFakeTagFormatterNotFoundRaisesException(self):
        with self.assertRaises(AttributeError):
            self.render("{% fake 'notFoundedFake' as foo %}")

    def testSimpleFakeTagOptionalAssignment(self):
        self.assertNotEqual(self.render("{% fake 'name' %}"), "")
        self.assertEqual(len(self.render("{% fake 'md5' %}")), 32)

    # do_fake_filter: fake
    def testFakeFilterTag(self):
        self.assertIn(self.render("{{ 'random_element'|fake:'test_string' }}"), 'test_string')

    def testFakeFilterWithValueFromContext(self):
        mylist = [100, 200, 300]
        rendered = self.render("{{ 'random_element'|fake:mylist }}", {'mylist': mylist})
        self.assertIn(rendered, [unicode(el) for el in mylist])

    def testFakeFilterFormatterNotFoundRaisesException(self):
        with self.assertRaises(AttributeError):
            self.render("{{ 'notFoundedFake'|fake:mylist }}", {'mylist': [100, 200, 300]})

    def testFakeFilterAsIfCondition(self):
        self.assertEqual(self.render("{% if 'boolean'|fake:100 %}True forever{% endif %}"), "True forever")
        self.assertEqual(self.render("{% if 'boolean'|fake:0 %}{% else %}False forever{% endif %}"), "False forever")

    def testFakeFilterAsForInRange(self):
        times = 10
        rendered = self.render("{% for word in 'words'|fake:times %}{{ word }}\n{% endfor %}", {'times': times})
        words = [word for word in rendered.split('\n') if word.strip()]
        self.assertEqual(len(words), times)

    # do_or_fake_filter: or_fake
    def testOrFakeFilterTag(self):
        self.assertEqual(len(self.render("{{ unknown_var|or_fake:'md5' }}")), 32)

    def testFullXmlContact(self):
        self.assertTrue(self.render("""<?xml version="1.0" encoding="UTF-8"?>
<contacts>
    {% fake 'random_int' 10 20 as times %}
    {% for i in 10|get_range %}
    <contact firstName="{% fake 'first_name' %}" lastName="{% fake 'last_name' %}" email="{% fake 'email' %}"/>
        <phone number="{% fake 'phone_number' %}"/>
        {% if 'boolean'|fake:25 %}
        <birth date="{{ 'date_time_this_century'|fake|date:"D d M Y" }}" place="{% fake 'city' %}"/>
        {% endif %}
        <address>
            <street>{% fake 'street_address' %}</street>
            <city>{% fake 'city' %}</city>
            <postcode>{% fake 'postcode' %}</postcode>
            <state>{% fake 'state' %}</state>
        </address>
        <company name="{% fake 'company' %}" catchPhrase="{% fake 'catch_phrase' %}">
        {% if 'boolean'|fake:25 %}
            <offer>{% fake 'bs' %}</offer>
        {% endif %}
        {% if 'boolean'|fake:33 %}
            <director name="{% fake 'name' %}" />
        {% endif %}
        </company>
        {% if 'boolean'|fake:15 %}
        <details>
        <![CDATA[
        {% fake 'text' 500 %}
        ]]>
        </details>
        {% endif %}
    </contact>
    {% endfor %}
</contacts>
"""))


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
