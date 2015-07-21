from __future__ import absolute_import

from abc import ABCMeta, abstractproperty, abstractmethod


class FieldInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self):
        """

        """

    @abstractmethod
    def serialize(self):
        """

        """


class TransformationInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def function(self, field, *args, **kwargs):
        """

        """


class HasFieldsMeta(ABCMeta):

    def __new__(metaclass, name, bases, attributes, *args, **kwargs):
        new_class = super(HasFieldsMeta, metaclass).__new__(
            metaclass, name, bases, attributes, *args, **kwargs
        )
        setattr(new_class, '_fields', {})
        setattr(new_class, '_field_names', [])
        for name in dir(new_class):
            attribute = getattr(new_class, name)
            if not isinstance(attribute,
                              (FieldInterface, TransformationInterface)):
                continue
            new_class._fields[name] = attribute
            new_class._field_names.append(name)
            attribute.field_name = name
        return new_class


class SchemaInterface(object):

    __metaclass__ = HasFieldsMeta

    @abstractmethod
    def validate(self):
        """

        """

    @abstractmethod
    def serialize(self):
        """

        """


class MappingInterface(object):

    __metaclass__ = HasFieldsMeta

    @property
    def source(self):
        """

        """

    @property
    def target(self):
        """

        """

    @abstractmethod
    def apply(self, blob):
        """

        """
