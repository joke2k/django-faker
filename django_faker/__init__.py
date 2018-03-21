"""
Django-faker uses a generator (eg faker) to generate test data for Django models and templates.
"""
from faker import Faker as FakerGenerator
from .populator import Populator


class DjangoFaker(object):

    instance = None
    populators = {}
    generators = {}

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(DjangoFaker, cls).__new__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        pass

    @staticmethod
    def get_codename(locale=None, providers=None):
        """
        codename = locale[-Provider]*
        """
        from django.conf import settings
        # language
        locale = locale or getattr(settings, 'FAKER_LOCALE', getattr(settings, 'LANGUAGE_CODE', None))
        # providers
        providers = providers or getattr(settings, 'FAKER_PROVIDERS', None)

        codename = locale or 'default'

        if providers:
            codename += "-" + "-".join(sorted(providers))

        return codename

    @classmethod
    def get_generator(cls, locale=None, providers=None, codename=None):
        """
        use a codename to cache generators
        """

        codename = codename or cls.get_codename(locale, providers)

        if codename not in cls.generators:
            # initialize with faker.generator.Generator instance
            # and remember in cache
            cls.generators[codename] = FakerGenerator(locale, providers)
            cls.generators[codename].seed(cls.generators[codename].random_int())

        return cls.generators[codename]

    @classmethod
    def get_populator(cls, locale=None, providers=None):
        """

        uses:

            from django_faker import DjangoFaker
            pop = DjangoFaker.get_populator()

            from myapp import models
            pop.add_entity(models.MyModel, 10)
            pop.add_entity(models.MyOtherModel, 10)
            pop.execute()

            pop = Faker.get_populator('it_IT')

            pop.add_entity(models.MyModel, 10)
            pop.add_entity(models.MyOtherModel, 10)
            pop.execute()

        """

        codename = cls.get_codename(locale, providers)

        if codename not in cls.populators:
            generator = cls.generators.get(codename, None) or cls.get_generator(codename=codename)

            cls.populators[codename] = Populator(generator)

        return cls.populators[codename]
