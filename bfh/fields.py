from datetime import datetime
from dateutil.parser import parse as parse_date

from .interfaces import FieldInterface


class Field(FieldInterface):

    def __init__(self, required=False):
        self.required = required

    def __get__(self, instance, cls=None):
        return instance.__dict__.get(self.field_name)

    def __set__(self, instance, value):
        instance.__dict__[self.field_name] = value

    def serialize(self, value):
        return value

    def validate(self, value):
        if self.required and value is None:
            return False
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
        pass


class SimpleTypeField(Field):

    def _validate(self, value):
        if not self.required and value is None:
            return True
        return isinstance(value, self.field_type)

    def validate(self):
        return super(SimpleTypeField, self).validate() and self._validate()


class IntegerField(SimpleTypeField):

    field_type = int


class NumberField(SimpleTypeField):

    field_type = float


class UnicodeField(SimpleTypeField):

    field_type = unicode


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
    """
    TODO is the coercion in the right place here??
    TODO keep the raw pre-coerced value around?
    """

    field_type = datetime

    def _coerce(self, value):
        if isinstance(value, int):
            return datetime.utcfromtimestamp(value)
        elif isinstance(value, basestring):
            return parse_date(value)

        else:
            raise TypeError("Could not coerce %s" % value)

    def serialize(self, value):
        return value.isoformat()
