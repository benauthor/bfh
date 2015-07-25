from __future__ import absolute_import

from .common import nullish
from .interfaces import SchemaInterface, MappingInterface

from . import fields
from . import transformations

__all__ = [
    "Schema",
    "Mapping",
    "fields",
    "transformations",
]


class Schema(SchemaInterface):
    """
    A base class for defining your schemas.

    Inherit this and add some fields:

        class Animal(Schema):
            name = UnicodeField()
            legs = IntegerField()
            noise = UnicodeField()

    """
    def __init__(self, *args, **kwargs):
        """
        Args:
           Pass a dictionary a single positional argument and it will be
           tranformed into kwargs.

        Kwargs:
           Values to assign to fields in the schema. Unknown names are ignored.
        """
        # when a dict is passed as positional argument, transform to kwargs
        if len(args) == 1 and isinstance(args[0], dict):
            return self.__init__(**dict(args[0], **kwargs))

        # stash raw kwargs for downstream
        # since this is set in metaclass, hidden from __dict__
        self._raw_input.update(kwargs)

        # init any subschemas
        for k, v in self._fields.items():
            if isinstance(v, fields.Subschema):
                setattr(self, k, v.subschema_class())

        # init values passed as kwargs
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def serialize(self, implicit_nulls=True):
        """
        Represent this schema as a dictionary.

        Kwargs:
            implicit_nulls (Bool) - drop any keys whose value is nullish

        Returns:
            dict
        """
        outd = {}
        for name in self._field_names:
            value = self.__dict__.get(name)
            field = self._fields.get(name)
            if hasattr(value, "serialize"):
                value = value.serialize(implicit_nulls=implicit_nulls)

            if hasattr(field, "serialize"):
                value = field.serialize(value)

            if implicit_nulls and nullish(value,
                                          implicit_nulls=implicit_nulls):
                pass
            else:
                outd[name] = value

        return outd

    def validate(self):
        """
        Validate the values in the schema.

        Returns:
            True

        Raises:
            Invalid
        """
        return all([v.validate(getattr(self, k))
                    for k, v in self._fields.items()])

    @property
    def is_empty(self):
        return all(nullish(v) for v in self.__dict__.values())


class GenericSchema(Schema):
    def __init__(self, as_dict):
        self.__dict__ = as_dict
        self._field_names = as_dict.keys()

    def __get__(self, name):
        if name not in self._field_names:
            return None
        return self.__dict__[name]

    def validate(self):
        return True


class Mapping(MappingInterface):

    def apply(self, blob):
        """
        This is going to take blob and create an instance of source schema.

        If no source schema is specified, use a generic schema.

        TODO validate (optionally) if source and target specified?
        """
        if self.source_schema is None:
            loaded_source = blob
        elif isinstance(blob, self.source_schema):
            loaded_source = blob
        else:
            loaded_source = self.source_schema(**blob)

        all_attrs = self._fields.keys()
        target_dict = {}
        for attr_name in all_attrs:
            transform = getattr(self, attr_name)
            result = transform(loaded_source)
            target_dict[attr_name] = result

        if self.target_schema is None:
            return GenericSchema(target_dict)

        return self.target_schema(**target_dict)
