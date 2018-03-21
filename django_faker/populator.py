from django.db.models import AutoField, ManyToManyField
from django.db.models.fields.reverse_related import ForeignObjectRel
from .constraints import validate_unique_constraint, validate_unique_together_constraint, \
    InvalidConstraint
from .guessers import NameGuesser, RelationGuesser, FieldTypeGuesser


class ModelPopulator(object):
    def __init__(self, model):
        """
        :param model: Generator
        """
        self.model = model
        self.field_formatters = {}

    def guess_field_formatters(self, generator):
        """
        Figure out how to populate the model's fields given a certain generator
        :param generator: should be able to create lots of types of fake values
        :return: a map of field name -> value generation function
        """
        formatters = {}
        model = self.model

        # field guesser order matters - whichever matches first has precedence
        field_guessers = [
            NameGuesser(generator),
            RelationGuesser(generator),
            FieldTypeGuesser(generator)
        ]

        for field in model._meta.get_fields():  # pylint: disable=protected-access
            # Skip auto fields because they'll be generated on insertion
            if isinstance(field, (AutoField, ForeignObjectRel)):
                continue

            # attempt to set
            for guesser in field_guessers:
                formatter = guesser.guess_format(field)
                if formatter:
                    formatters[field.name] = formatter
                    break

            if not formatters[field.name]:
                # No formatter set, something weird must've happened
                raise AttributeError(field)

        return formatters

    def execute(self, using, inserted_entities):
        obj = self.model()
        # try up to 1000 times to create an acceptable object
        # Ideally, we'd generate an acceptable list of unique fields/tuples of unique together fields
        # But that is harder when dealing with all sorts of generic fields, relational fields, etc
        # A good future improvement
        count = 0
        while count < 1000:
            many_fields = {}
            for field, fmt in self.field_formatters.items():
                if fmt:
                    value = fmt(inserted_entities) if hasattr(fmt, '__call__') else fmt
                    if isinstance(self.model._meta.get_field(field),  # pylint: disable=protected-access
                                  ManyToManyField):
                        if value:
                            many_fields[field] = value
                    else:
                        setattr(obj, field, value)
            try:
                validate_unique_constraint(obj)
                validate_unique_together_constraint(obj)
                obj.save(using=using)
                # set many to many once id is created
                for field, val in many_fields.items():
                    getattr(obj, field).set(val)
                obj.save(using=using)
                return obj.pk
            except InvalidConstraint as e:
                if count == 1000:
                    raise e
            count += 1


class Populator(object):
    def __init__(self, generator):
        """
        :param generator: Generator
        """
        self.generator = generator
        self.entities = {}
        self.quantities = {}
        self.orders = []

    def add_entity(self, model, number, custom_field_formatters=None):
        """
        Add an order for the generation of $number records for $entity.

        :param model: mixed A Django Model classname, or a faker.orm.django.EntityPopulator instance
        :type model: Model
        :param number: int The number of entities to populate
        :type number: integer
        :param custom_field_formatters: optional dict with field as key and callable as value
        :type custom_field_formatters: dict or None
        """
        if not isinstance(model, ModelPopulator):
            model = ModelPopulator(model)

        model.field_formatters = model.guess_field_formatters(self.generator)
        if custom_field_formatters:
            model.field_formatters.update(custom_field_formatters)

        klass = model.model
        self.entities[klass] = model
        self.quantities[klass] = number
        self.orders.append(klass)

    def execute(self, using=None):
        """
        Populate the database using all the Entity classes previously added.

        :param using A Django database connection name
        :rtype: A list of the inserted PKs
        """
        if not using:
            using = self.get_connection()

        inserted_entities = {}
        for klass in self.orders:
            number = self.quantities[klass]
            if klass not in inserted_entities:
                inserted_entities[klass] = []
            for _ in range(0, number):
                inserted_entities[klass].append(self.entities[klass].execute(using, inserted_entities))

        return inserted_entities

    def get_connection(self):
        """
        use the first connection available
        :rtype: Connection
        """

        klass = self.entities.keys()
        if not klass:
            raise AttributeError('No class found from entities. Did you add entities to the Populator ?')
        klass = list(klass)[0]

        return klass.objects._db  # pylint: disable=protected-access

    def clear(self):
        self.entities = {}
        self.quantities = {}
        self.orders = []
