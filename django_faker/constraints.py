# Credit for constraints goes to django-autofixture:
# https://github.com/gregmuellegger/django-autofixture/blob/master/autofixture/constraints.py
# Copyright (c) 2010, Gregor Müllegger
# All rights reserved.

from django.db.models.fields import related


class InvalidConstraint(Exception):
    def __init__(self, fields, *args, **kwargs):
        self.fields = fields
        super(InvalidConstraint, self).__init__(*args, **kwargs)


def _is_unique_field(field):
    if not field.unique:
        return False
    if field.primary_key:
        # Primary key fields should not generally be checked for unique constraints, except when the
        # primary key is a OneToOne mapping to an external table not via table inheritance, in which
        # case we don't want to create new objects which will overwrite existing objects.
        return (isinstance(field, related.OneToOneField) and
                not issubclass(field.model, field.remote_field.model))
    return True


def validate_unique_constraint(instance):
    error_fields = []
    for field in instance._meta.fields:  # pylint: disable=protected-access
        if _is_unique_field(field):
            value = getattr(instance, field.name)

            # If the value is none and the field allows nulls, skip it
            if value is None and field.null:
                continue

            check = {field.name: value}

            if instance._meta.default_manager.filter(**check).exists():  # pylint: disable=protected-access
                error_fields.append(field)
    if error_fields:
        raise InvalidConstraint(error_fields)


def validate_unique_together_constraint(instance):
    if not instance._meta.unique_together:  # pylint: disable=protected-access
        return
    error_fields = []
    for unique_fields in instance._meta.unique_together:  # pylint: disable=protected-access
        check = {}
        for field_name in unique_fields:
            if not instance._meta.get_field(field_name).primary_key:  # pylint: disable=protected-access
                check[field_name] = getattr(instance, field_name)
        if all(e is None for e in check.values()):
            continue

        if instance._meta.default_manager.filter(**check).exists():  # pylint: disable=protected-access
            error_fields.extend([
                instance._meta.get_field(field_name)  # pylint: disable=protected-access
                for field_name in unique_fields
            ])
    if error_fields:
        raise InvalidConstraint(error_fields)
