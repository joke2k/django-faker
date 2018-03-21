import random
import re
import pytz
from django.db.models import ForeignKey, ManyToManyField, OneToOneField, ImageField, FileField, \
    PositiveSmallIntegerField, BigIntegerField, SmallIntegerField, PositiveIntegerField, IntegerField, DecimalField, \
    FloatField, SlugField, URLField, EmailField, TextField, UUIDField, CharField, BinaryField, BooleanField, \
    NullBooleanField, DateField, DateTimeField, DurationField, TimeField, FilePathField, GenericIPAddressField
from constraints import InvalidConstraint


class FieldGuesser(object):
    """
    Used to determine how to handle a given field
    """
    def __init__(self, generator):
        """
        :param generator Generator
        """
        self.generator = generator

    def guess_format(self, field):
        """
        :param field:
        :type field: Django Model Field
        Field Guessers attempt to return:
            b. a function to generate a value given a set of inserted objects
        """
        raise NotImplementedError('Subclass Guesser and implement this')


class NameGuesser(FieldGuesser):
    def guess_format(self, field): # pylint: disable=too-many-return-statements,too-many-branches
        # Don't try to deal with relational fields or fields with choices
        if isinstance(field, (ForeignKey, ManyToManyField, OneToOneField)) or field.choices:
            return
        generator = self.generator

        name = field.name
        name = name.lower()
        if re.findall(r'^is[_A-Z]', name):
            return lambda x: generator.boolean()
        if re.findall(r'(_a|A)t$', name):
            return lambda x: generator.date_time(tzinfo=pytz.UTC)
        if name in ('first_name', 'firstname'):
            return lambda x: generator.first_name()
        if name in ('last_name', 'lastname'):
            return lambda x: generator.last_name()
        if name == 'name':
            return lambda x: generator.word()
        if name in ('username', 'login', 'nickname'):
            return lambda x: generator.user_name()
        if name in ('email', 'email_address'):
            return lambda x: generator.email()
        if name in ('phone_number', 'phonenumber', 'phone'):
            return lambda x: generator.phone_number()
        if name == 'address':
            return lambda x: generator.address()
        if name == 'city':
            return lambda x: generator.city()
        if name in ('streetaddress', 'street_address'):
            return lambda x: generator.street_address()
        if name in ('postcode', 'zipcode'):
            return lambda x: generator.postcode()
        if name == 'state':
            return lambda x: generator.state_abbr()
        if name == 'country':
            return lambda x: generator.country()
        if name == 'title':
            return lambda x: generator.sentence()
        if name in ('body', 'summary', 'description'):
            return lambda x: generator.paragraph()


class RelationGuesser(FieldGuesser):
    def guess_format(self, field):
        if isinstance(field, (ForeignKey, ManyToManyField, OneToOneField)):
            return relation_wrapper(field)


def relation_wrapper(local_field):
    def build_relation(inserted):
        related_model = local_field.remote_field.model
        # Try to choose from the recently created
        if related_model in inserted and inserted[related_model]:
            choices = inserted[related_model]
            if isinstance(local_field, OneToOneField):
                # Only allow unused related model primary keys
                unused = {
                    local_field.related_query_name(): None
                }
                allowed = related_model.objects.filter(**unused)
                choices = [obj.pk for obj in allowed if obj.pk in inserted[related_model]]
            if choices:
                if isinstance(local_field, ManyToManyField):
                    num = random.randint(1, len(choices))
                    random.shuffle(choices)
                    return related_model.objects.filter(pk__in=choices[0:num])
                return related_model.objects.get(pk=random.choice(choices))

        # Try to choose from already created objects
        choices = related_model.objects.all()
        if isinstance(local_field, OneToOneField):
            unused = {
                local_field.related_query_name(): None
            }
            choices = related_model.objects.filter(**unused)
            choices = choices.order_by('?')
        if not choices:
            if local_field.null or local_field.blank:
                return None
            raise InvalidConstraint(
                'Relation "%s.%s" with "%s" cannot be null. Check order of addEntity list and '
                'that there are enough objects for one-to-one relations' % (
                    local_field.model.__name__, local_field.name, related_model.__name__,
                ))
        if isinstance(local_field, ManyToManyField):
            num = random.randint(1, len(choices))
            return choices[:num]
        return choices[0]

    return build_relation


class FieldTypeGuesser(FieldGuesser):
    def guess_format(self, field):  # pylint: disable=too-many-return-statements,too-many-branches
        generator = self.generator
        if field.choices:
            return lambda x: generator.random_element(field.choices)[0]

        if isinstance(field, PositiveSmallIntegerField):
            return lambda x: generator.random_int(0, 32767)
        if isinstance(field, BigIntegerField):
            return lambda x: generator.random_int(-9223372036854775808, 9223372036854775807)
        if isinstance(field, SmallIntegerField):
            return lambda x: generator.random_int(0, 65535)
        if isinstance(field, PositiveIntegerField):
            return lambda x: generator.random_int(0, 2147483647)
        if isinstance(field, IntegerField):
            return lambda x: generator.random_int(-2147483648, 2147483647)

        if isinstance(field, DecimalField):
            return lambda x: generator.pydecimal(left_digits=field.max_digits - field.decimal_places,
                                                 right_digits=field.decimal_places)
        if isinstance(field, FloatField):
            return lambda x: generator.pyfloat(left_digits=field.max_digits - field.decimal_places,
                                               right_digits=field.decimal_places)

        if isinstance(field, SlugField):
            return lambda x: generator.slug()
        if isinstance(field, URLField):
            return lambda x: generator.uri()
        if isinstance(field, EmailField):
            return lambda x: generator.email()
        if isinstance(field, TextField):
            return lambda x: generator.paragraph()
        if isinstance(field, UUIDField):
            return lambda x: generator.uuid4()
        if isinstance(field, CharField):
            return lambda x: generator.text(field.max_length) if field.max_length >= 5 else generator.word()

        if isinstance(field, BinaryField):
            return lambda x: generator.binary(length=1048576)  # limit for performance
        if isinstance(field, BooleanField):
            return lambda x: generator.boolean()
        if isinstance(field, NullBooleanField):
            return lambda x: generator.null_boolean()

        if isinstance(field, DateField):
            return lambda x: generator.date()
        if isinstance(field, DateTimeField):
            return lambda x: generator.date_time(tzinfo=pytz.UTC)
        if isinstance(field, DurationField):
            return lambda x: generator.time_delta()
        if isinstance(field, TimeField):
            return lambda x: generator.time()

        if isinstance(field, ImageField):
            return lambda x: None
        if isinstance(field, FileField):
            return lambda x: None
        if isinstance(field, FilePathField):
            return lambda x: "/"

        if isinstance(field, GenericIPAddressField):
            protocolIp = generator.random_elements(['ipv4', 'ipv6'])
            return lambda x: getattr(generator, protocolIp)()
