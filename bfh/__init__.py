from __future__ import absolute_import

from .interfaces import SchemaInterface, MappingInterface, NULLISH

from . import fields
from . import transformations

__all__ = [
    "Schema",
    "Mapping",
    "fields",
    "transformations",
]


class Schema(SchemaInterface):

    def __init__(self, *args, **kwargs):
        # when a dict is passed as positional argument, transform to kwargs
        if len(args) == 1 and isinstance(args[0], dict):
            return self.__init__(**dict(args[0], **kwargs))

        # init any subschemas
        for k, v in self._fields.items():
            if isinstance(v, fields.Subschema):
                setattr(self, k, v.subschema_class())

        # init values passed as kwargs
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def serialize(self, implicit_nulls=True):
        outd = {}
        for name in self._field_names:
            value = self.__dict__.get(name)
            field = self._fields.get(name)
            if hasattr(value, "serialize"):
                value = value.serialize(implicit_nulls=implicit_nulls)

            if hasattr(field, "serialize"):
                value = field.serialize(value)

            if implicit_nulls and value in NULLISH:
                pass
            else:
                outd[name] = value

        return outd

    def validate(self):
        return all([v.validate(getattr(self, k))
                    for k, v in self._fields.items()])

    @property
    def is_empty(self):
        return all(v in NULLISH for v in self.__dict__.values())


class GenericSchema(Schema):
    def __init__(self, as_dict):
        self.__dict__ = as_dict
        self._field_names = as_dict.keys()

    def __get__(self, name):
        if name not in self._field_names:
            return None
        return self.__dict__[name]

    def validate(self):
        pass


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
