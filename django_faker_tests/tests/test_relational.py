from django import test
from django_faker import DjangoFaker
from django_faker.constraints import InvalidConstraint
from ..models import One, ToOne, Many, ToMany, Foreign, Key


class RelationalTestCse(test.TestCase):

    def setUp(self):
        populator = DjangoFaker.get_populator()
        populator.clear()

    def test_one_to_one(self):
        """Should preserve the one-to-one constraint (each one should have a different to one)"""
        populator = DjangoFaker.get_populator()
        populator.add_entity(ToOne, 5)
        populator.add_entity(One, 5)
        populator.execute()
        to_ones = ToOne.objects.all()
        for one in One.objects.all():
            to_ones = to_ones.exclude(one=one)
        self.assertEqual(0, len(to_ones))

    def test_one_to_one_fail(self):
        """Should throw an exception if """
        try:
            populator = DjangoFaker.get_populator()
            populator.add_entity(ToOne, 4)
            populator.add_entity(One, 5)
            populator.execute()
            self.fail("each One should need an unused ToOne which should be impossible here")
        except InvalidConstraint:
            pass

    def test_one_to_one_existing(self):
        """Should be able to use a mix of existing db and new entities"""
        populator = DjangoFaker.get_populator()
        to_one = ToOne(thing='stuff')
        to_one.save()
        populator.add_entity(ToOne, 1)
        populator.add_entity(One, 2)
        populator.execute()
        to_ones = ToOne.objects.all()
        for one in One.objects.all():
            to_ones = to_ones.exclude(one=one)
        self.assertEqual(0, len(to_ones))

    def test_many_to_many(self):
        """Each many-to-many field assigns 1 or more object if they exist.
        many-to-many fields won't error out if there are no available objects"""
        populator = DjangoFaker.get_populator()
        populator.add_entity(ToMany, 5)
        populator.add_entity(Many, 5)
        populator.execute()
        for many in Many.objects.all():
            self.assertTrue(len(many.to_many.all()) > 0)

    def test_many_to_many_fail(self):
        """Non-null many-to-many fields will raise exceptions if there aren't available objects"""
        try:
            populator = DjangoFaker.get_populator()
            populator.add_entity(Many, 1)
            populator.execute()
            self.fail("All Many's require at least one ToMany to exist")
        except InvalidConstraint:
            pass

    def test_many_to_many_existing(self):
        """Should be able to use existing db values if none added to populator"""
        populator = DjangoFaker.get_populator()
        to_many = ToMany(thing='stuff')
        to_many.save()
        populator.add_entity(Many, 1)
        populator.execute()
        self.assertEqual(1, len(Many.objects.all()))

    def test_foreign_key(self):
        """Should be able to use one key for all the foreigns"""
        populator = DjangoFaker.get_populator()
        populator.add_entity(Key, 1)
        populator.add_entity(Foreign, 5)
        populator.execute()
        self.assertEqual(5, len(Key.objects.all()[0].foreigns.all()))
