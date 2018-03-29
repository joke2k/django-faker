from django import test
from django.template import Context
from django.template import Template


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
        self.assertIn(rendered, [str(el) for el in mylist])

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
