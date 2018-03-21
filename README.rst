Django-faker
============

*Django-faker* uses `faker`_ package to generate test data for Django models and templates.

|pypi| |unix_build| |windows_build| |coverage| |downloads| |license|

How to use
----------

To install Django-faker you can use pip::

    pip install django-faker


Configuration
~~~~~~~~~~~~~

In django application `settings.py`::

    INSTALLED_APPS = (
        # ...
        'django_faker',
    )

    FAKER_LOCALE = None     # settings.LANGUAGE_CODE is loaded
    FAKER_PROVIDERS = None  # faker.DEFAULT_PROVIDERS is loaded (all)


Populating Django Models
~~~~~~~~~~~~~~~~~~~~~~~~

*Django-faker* provides an adapter for Django Models, for easy population of test databases.
To populate with Model instances, create a new Populator class,
then list the class and number of all of Models that must be generated. To launch the actual data population,
call `execute()` method.

Here is an example showing how to populate 5 `Game` and 10 `Player` objects::

    from django_faker import Faker
    # this Populator is only a function thats return a django_faker.populator.Populator instance
    # correctly initialized with a faker.generator.Generator instance, configured as above
    populator = Faker.get_populator()

    from myapp.models import Game, Player
    populator.add_entity(Game,5)
    populator.add_entity(Player,10)

    insertedPks = populator.execute()

The populator uses name and column type guessers to populate each column with relevant data.
For instance, Django-faker populates a column named `first_name` using the `first_name` formatter, and a column with
a `datetime` instance using the `date_time`.
The resulting entities are therefore coherent. If Django-faker misinterprets a column name, you can still specify a custom
function to be used for populating a particular column, using the third argument to `add_entity()`::


    populator.add_entity(Player, 10, {
        'score':    lambda x: populator.generator.random_int(0,1000),
        'nickname': lambda x: populator.generator.email(),
    })
    populator.execute()

Of course, Django-faker does not populate autoincremented primary keys.
In addition, `django_faker.populator.Populator.execute()` returns the list of inserted PKs, indexed by class::

    print insertedPks
    {
        <class 'faker.django.tests.Player'>: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        <class 'faker.django.tests.Game'>: [1, 2, 3, 4, 5]
    }

In the previous example, the `Player` and `Game` models share a relationship. Since `Game` entities are populated first,
Faker is smart enough to relate the populated `Player` entities to one of populated `Game` entities.


Relational Fields
------------------------

Django-faker will attempt to populate relational fields in the following manner:
1. From model instances added through `add_entity()`
2. From pre-existing values in the db

If there aren't available values and the field can't be null, an `AttributeError` is thrown

**One-to-one fields**
The Populator keeps track of what values have been used already so it doesn't violate the one-to-one constraint

**Many-to-many fields**
The Populator randomly selects between 1-n values to assign to the object

**Foreign key fields**
The Populator randomly selects 1 value to assign

**unique/unique_together constraints**
Currently, django-faker tries to populate the field(s) and then if a constraint is violated it tries again.
This happens up to 1000 times and then an InvalidConstraint exception is thrown.
Future iterations will hopefully pick values from a generated set of options to guarantee correctness.


Template tags and filter
~~~~~~~~~~~~~~~~~~~~~~~~

Django-faker offers a useful template tags and filters for interact with `PyFaker`_::

    {% fake 'name' as myname %}{% fake 'date_time_between' '-10d' as mydate %}

    {{ myname|title }} - {{ mydate|date:"M Y" }}



    {% load fakers %}

    <?xml version="1.0" encoding="UTF-8"?>
    <contacts>
        {% fake 'random_int' 10 20 as times %}
        {% for i in 10|get_range %}
        <contact first_name="{% fakestr 'first_name' %}" last_name="{% fakestr 'last_name' %}" email="{% fakestr 'email' %}"/>
            <phone number="{% fakestr 'phone_number' %}"/>
            {% if 'boolean'|fake:25 %}
            <birth date="{{ 'date_time_this_century'|fake|date:"D d M Y" }}" place="{% fakestr 'city' %}"/>
            {% endif %}
            <address>
                <street>{% fakestr 'street_address' %}</street>
                <city>{% fakestr 'city' %}</city>
                <postcode>{% fakestr 'postcode' %}</postcode>
                <state>{% fakestr 'state' %}</state>
            </address>
            <company name="{% fakestr 'company' %}" catch_phrase="{% fakestr 'catch_phrase' %}">
            {% if 'boolean'|fake:25 %}
                <offer>{% fakestr 'bs' %}</offer>
            {% endif %}
            {% if 'boolean'|fake:33 %}
                <director name="{% fakestr 'name' %}" />
            {% endif %}
            </company>
            {% if 'boolean'|fake:15 %}
            <details>
            <![CDATA[
            {% fakestr 'text' 500 %}
            ]]>
            </details>
            {% endif %}
        </contact>
        {% endfor %}
    </contacts>


Page preview
~~~~~~~~~~~~
Open `url.py` in your main application and add this url::

    urlpatterns = patterns('',
        ...
        url(r'', include('django_faker.urls')),
        ...
    )

http://127.0.0.1:8000/preview/ shows a faked browser windows, useful for screenshots.

Running the Tests
-----------------

Run django tests in a django environment:

    $ python runtests.py

or if you have 'django_faker' in INSTALLED_APPS:

    $ python manage.py test django_faker


Changelog
---------

`0.3dev <http://github.com/joke2k/django-faker/compare/v0.2...master>`__
------------------------------------------------------------------------

- Upgrade fake-factory version

`0.2 - 23-January-2013 <http://github.com/joke2k/django-faker/compare/v0.1...v0.2>`__
-------------------------------------------------------------------------------------

- Add requirements
- Fake browser preview

0.1 - 01-December-2012
----------------------

- Add django Model instance generator
- Add django template tag and filter


.. _faker: https://www.github.com/joke2k/faker/

.. |pypi| image:: https://img.shields.io/pypi/v/django-faker.svg?style=flat-square&label=version
    :target: https://pypi.python.org/pypi/django-faker
    :alt: Latest version released on PyPi

.. |coverage| image:: https://img.shields.io/coveralls/joke2k/django-faker/master.svg?style=flat-square
    :target: https://coveralls.io/r/joke2k/django-faker?branch=master
    :alt: Test coverage

.. |unix_build| image:: https://img.shields.io/travis/joke2k/django-faker/master.svg?style=flat-square&label=unix%20build
    :target: http://travis-ci.org/joke2k/django-faker
    :alt: Build status of the master branch on Mac/Linux

.. |windows_build|  image:: https://img.shields.io/appveyor/ci/joke2k/django-faker.svg?style=flat-square&label=windows%20build
    :target: https://ci.appveyor.com/project/joke2k/django-faker
    :alt: Build status of the master branch on Windows

.. |downloads| image:: https://img.shields.io/pypi/dm/django-faker.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-faker
    :alt: Monthly downloads

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://raw.githubusercontent.com/joke2k/django-faker/master/LICENSE.txt
    :alt: Package license
