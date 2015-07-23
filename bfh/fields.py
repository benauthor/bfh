from __future__ import absolute_import

from datetime import datetime

from .exceptions import Invalid
from .interfaces import FieldInterface, SchemaInterface

try:
    string_type = unicode
except NameError:
    string_type = str


__all__ = [
    "BooleanField",
    "Field",
    "Subschema",
    "IntegerField",
    "NumberField",
    "ObjectField",
    "ArrayField",
    "UnicodeField",
    "DatetimeField",
]


class Field(FieldInterface):

    def __init__(self, required=True):
        self.required = required

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        return instance.__dict__.get(self.field_name)

    def __set__(self, instance, value):
        instance.__dict__[self.field_name] = value

    def serialize(self, value):
        return value

    def validate(self, value):
        if self.required and value is None:
            raise Invalid("%s: a value is required" % self.field_name)
        return True

    @property
    def field_name(self):
        return getattr(self, "_field_name", "unnamed")

    @field_name.setter
    def field_name(self, value):
        self._field_name = value


class Subschema(Field):
    """

    """
    def __init__(self, subschema_class, *args, **kwargs):
        super(Subschema, self).__init__(*args, **kwargs)
        self.subschema_class = subschema_class

    def __set__(self, instance, value):
        if isinstance(value, dict):
            instance.__dict__[self.field_name] = self.subschema_class(**value)
        else:
            instance.__dict__[self.field_name] = value

    def serialize(self, value):
        if hasattr(value, "serialize"):
            value = value.serialize()

        if value is None:
            value = {}

        if not self.required:
            if all(v in (None, [], {}, '') for v in value.values()):
                value = {}

        return value

    def validate(self, value):
        super(Subschema, self).validate(value)
        if not self.required and value is None:
            return True
        value.validate()
        return True


class SimpleTypeField(Field):

    def _valid(self, value):
        if value is None and not self.required:
            return True
        return isinstance(value, self.field_type)

    def validate(self, value):
        super(SimpleTypeField, self).validate(value)
        if not self._valid(value):
            raise Invalid("%s: %s is not a valid %s" % (self.field_name,
                                                        value,
                                                        self.field_type))
        return True


class BooleanField(SimpleTypeField):

    field_type = bool


class IntegerField(SimpleTypeField):

    field_type = int


class NumberField(SimpleTypeField):

    field_type = float


class UnicodeField(SimpleTypeField):

    field_type = string_type

    def __init__(self, strict=False, **kwargs):
        super(UnicodeField, self).__init__(**kwargs)
        self.strict = strict

    def _coerce(self, value):
        if isinstance(value, string_type):
            return value
        try:
            return value.decode('utf-8')
        except AttributeError:
            raise Invalid("%s: %s is not a string" % (self.field_name, value))

    def validate(self, value):
        if self.strict or (value is None and not self.required):
            return super(UnicodeField, self).validate(value)
        return super(UnicodeField, self).validate(self._coerce(value))

    def serialize(self, value):
        try:
            return self._coerce(value)
        except Invalid:  # we are not in the business of validation here
            return value


class ObjectField(SimpleTypeField):

    field_type = (dict, SchemaInterface)

    def validate(self, value):
        super(ObjectField, self).validate(value)
        if hasattr(value, "validate"):
            value.validate()
        return True

    def serialize(self, value):
        if hasattr(value, "serialize"):
            value = value.serialize()

        if value is None:
            value = {}

        if not self.required:
            if all(v in (None, [], {}, '') for v in value.values()):
                value = {}

        return value


class ArrayField(SimpleTypeField):
    """
    N.B. array_type is a class, not an instance
    """
    field_type = (list, tuple)

    def __init__(self, array_type=None, **kwargs):
        super(ArrayField, self).__init__(**kwargs)
        self.array_type = array_type

    def _flatten(self, value):
        if hasattr(value, 'serialize'):
            return value.serialize()
        return value

    @property
    def is_schema_type(self):
        return issubclass(self.array_type, SchemaInterface)

    def validate(self, items):
        # blech... it's not a validation lib. it's not a validation lib.
        super(ArrayField, self).validate(items)
        if not self.required and items in (None, [], tuple()):
            return True

        if self.is_schema_type:
            for val in items:
                if isinstance(val, self.array_type):
                    return val.validate()
                if isinstance(val, SchemaInterface):  # wrong schema
                    raise Invalid("%s is not a %s" % (val, self.array_type))

                # val is an object literal. see if it matches schema.
                in_schema = self.array_type(val)
                return in_schema.validate()

        elif self.array_type is not None and items is not None:
            for val in items:
                if not isinstance(val, self.array_type):
                    raise Invalid("%s is not a %s" % (val, self.array_type))

        return True

    def serialize(self, value):
        if isinstance(value, self.field_type):
            return [self._flatten(i) for i in value]
        return value


class DatetimeField(SimpleTypeField):

    field_type = datetime


class IsoDateString(DatetimeField):

    def serialize(self, value):
        try:
            return value.isoformat()
        except AttributeError:
            return value
