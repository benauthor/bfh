from __future__ import absolute_import

from .exceptions import Missing
from .interfaces import TransformationInterface

try:
    string_type = unicode
except NameError:
    string_type = str

__all__ = [
    "All",
    "Get",
    "Const",
    "Concat",
    "Bool",
    "Num",
    "Do",
    "Int",
    "Str",
]


class All(TransformationInterface):
    def __init__(self):
        pass

    def __call__(self, source):
        return self.function(source)

    def function(self, source):
        return source


class Get(TransformationInterface):
    """
    Gets a value from a dict or object

        value = Get("my_thing")({"my_thing": "get this"})
        value == "get this"

    Fetch values from complex objects by passing multiple arguments.

        value = Get("a", "b")({"a": {"b": 1}})
        value == 1

    kwargs:
        optional (bool) -- don't error if names missing, just return None

    returns:
        fetched value or None if `optional` kwarg is set

    raises:
        Missing if `optional` kwarg is false
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, source):
        return self.function(source)

    @property
    def path(self):
        return self.args

    @property
    def optional(self):
        return self.kwargs.get('optional')

    def _get_from_dict(self, source, path):
        if self.optional:
            return source.get(path)
        return source[path]

    def _get_from_obj(self, source, path):
        if self.optional:
            return getattr(source, path, None)
        return getattr(source, path)

    def _get(self, source, path):
        try:
            if isinstance(source, dict):
                return self._get_from_dict(source, path)
            return self._get_from_obj(source, path)
        except (KeyError, AttributeError) as e:
            raise Missing(e)

    def function(self, source, path=None):
        parts = path or self.path
        first, rest = parts[0], parts[1:]
        got = self._get(source, first)
        if rest:
            return self.function(got, rest)
        return got


class Transformation(TransformationInterface):
    """
    A callable thing that transforms an input.

    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, source=None):
        new_args = []
        for arg in self.args:
            if isinstance(arg, TransformationInterface):
                new_args.append(arg(source))
            else:
                new_args.append(arg)

        self.args = new_args
        return self.function(source)


class Const(Transformation):
    @property
    def value(self):
        return self.args[0]

    def function(self, source=None):
        return self.value


class CoerceType(Transformation):
    """
    A transformation that uses basic Python type coercion

    """

    @property
    def target_type(self):
        raise NotImplementedError("Specify a type")

    @property
    def value(self):
        return self.args[0]

    def function(self, source=None):
        return self.target_type(self.value)


class Int(CoerceType):

    target_type = int


class Num(CoerceType):

    target_type = float


class Str(CoerceType):

    target_type = string_type


class Bool(CoerceType):

    target_type = bool


class Concat(Transformation):

    def function(self, source=None):
        return "".join(self.args)


class Do(Transformation):

    @property
    def to_call(self):
        return self.args[0]

    @property
    def call_args(self):
        return self.args[1:]

    def function(self, source=None):
        return self.to_call(*self.call_args)
