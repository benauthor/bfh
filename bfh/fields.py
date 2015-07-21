from datetime import datetime
from dateutil.parser import parse as parse_date

from .exceptions import Invalid
from .interfaces import FieldInterface

__all__ = [
    "BooleanField",
    "Field",
    "Subschema",
    "IntegerField",
    "NumberField",
    "DictField",
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
            raise Invalid("A value is required")
        return True


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
        return value.serialize()

    def validate(self, value):
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
            raise Invalid("%s is not a valid %s" % (value, self.field_type))
        return True


class BooleanField(SimpleTypeField):

    field_type = bool


class IntegerField(SimpleTypeField):

    field_type = int


class NumberField(SimpleTypeField):

    field_type = float


class UnicodeField(SimpleTypeField):

    field_type = unicode

    def __init__(self, strict=False, **kwargs):
        super(UnicodeField, self).__init__(**kwargs)
        self.strict = strict

    @staticmethod
    def _coerce(value):
        if isinstance(value, unicode):
            return value
        try:
            return value.decode('utf-8')
        except AttributeError:
            raise Invalid("%s is not a string" % value)

    def validate(self, value):
        if self.strict:
            return super(UnicodeField, self).validate(value)
        return super(UnicodeField, self).validate(self._coerce(value))

    def serialize(self, value):
        if self.strict:
            return value
        return self._coerce(value)


class DictField(SimpleTypeField):

    field_type = dict


class ArrayField(SimpleTypeField):

    field_type = list

    def _flatten(self, value):
        if hasattr(value, 'serialize'):
            return value.serialize()
        return value

    def serialize(self, value):
        return [self._flatten(i) for i in value]


class DatetimeField(SimpleTypeField):

    field_type = datetime


class IsoDateString(DatetimeField):

    def serialize(self, value):
        return value.isoformat()

#     def _coerce(self, value):
#         if isinstance(value, int):
#             return datetime.utcfromtimestamp(value)
#         elif isinstance(value, basestring):
#             return parse_date(value)

#         else:
#             raise TypeError("Could not coerce %s" % value)
