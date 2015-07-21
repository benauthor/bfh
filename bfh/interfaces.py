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
        if name == "Schema3":
            import ipdb;ipdb.set_trace()
        for name in dir(new_class):
            attribute = getattr(new_class, name)
            if not isinstance(attribute,
                              (FieldInterface, TransformationInterface)):
                continue
            new_class._fields[name] = attribute
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
