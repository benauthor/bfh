from __future__ import absolute_import

from datetime import datetime, timedelta, tzinfo
from dateutil.parser import parse as parse_date

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
    "ManySubmap",
    "Num",
    "Do",
    "Int",
    "Str",
    "Submapping",
]


class UTC(tzinfo):

    OFFSET = timedelta(0)

    def utcoffset(self, dt):
        return self.OFFSET

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.OFFSET

utc = UTC()


class All(TransformationInterface):
    def __init__(self):
        pass

    def __call__(self, source):
        return self.function(source)

    def function(self, source):
        if hasattr(source, "serialize"):
            return source.serialize()
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
        required (bool, default False) -- error if names missing

    returns:
        fetched value or None if `required`

    raises:
        Missing if `required` is false
    """
    def __init__(self, *args, **kwargs):
        self.path = args
        self.kwargs = kwargs
        if kwargs.get('required') is None:
            self.required = False
        else:
            self.required = kwargs.get('required')

    def __call__(self, source):
        return self.function(source)

    def _get_from_dict(self, source, path):
        if not self.required:
            return source.get(path)
        return source[path]

    def _get_from_obj(self, source, path):
        if not self.required:
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
        if kwargs.get('required') is None:
            self.required = False
        else:
            self.required = kwargs.get('required')

    def __call__(self, source=None):
        call_args = []
        for arg in self.args:
            if isinstance(arg, TransformationInterface):
                call_args.append(arg(source))
            else:
                call_args.append(arg)

        # self.args = new_args
        return self.function(source, *call_args)


class Submapping(Transformation):

    def __init__(self, submapping_class, *args):
        self.submapping_class = submapping_class
        self.args = args

    def function(self, source, *call_args):  # source ignored
        return self.submapping_class().apply(call_args[0])


def _many_items(call_args):
    if len(call_args) > 1:
        return call_args

    if len(call_args) == 1 and isinstance(call_args[0], (list, tuple)):
        return call_args[0]

    elif len(call_args) == 1:
        return [call_args[0]]

    else:
        return []


class ManySubmap(Submapping):

    def function(self, source, *call_args):  # source ignored
        return [self.submapping_class().apply(item).serialize()
                for item in _many_items(call_args)]


class Many(Transformation):

    def __init__(self, subtrans, *args, **kwargs):
        self.subtrans = subtrans  # Transformation
        self.args = args
        self.kwargs = kwargs

    def function(self, source, *call_args):
        if isinstance(self.subtrans, Submapping):
            raise ValueError("Can't Many(Submapping). Use Manymap instead.")

        return [self.subtrans(item, **self.kwargs)()
                for item in _many_items(call_args)]


class Const(Transformation):

    def function(self, source, *call_args):  # source ignored
        return call_args[0]


class CoerceType(Transformation):
    """
    A transformation that uses basic Python type coercion

    """

    null_types = (None,)

    @property
    def target_type(self):
        raise NotImplementedError("Specify a type")

    def function(self, source, *call_args):  # source ignored
        value = call_args[0]
        if not self.required and value in self.null_types:
            return value
        return self.target_type(value)


class Int(CoerceType):

    target_type = int


class Num(CoerceType):

    target_type = float


class Str(CoerceType):

    target_type = string_type

    null_types = (None, "")


class Bool(CoerceType):

    target_type = bool


class Concat(Transformation):

    def function(self, source, *call_args):  # source ignored
        return "".join(call_args)


class Do(Transformation):

    def function(self, source, *call_args):  # source ignored
        return call_args[0](*call_args[1:])


class ParseDate(Transformation):

    DEFAULT_TIMEZONE = utc

    @property
    def tz(self):
        return self.kwargs.get("tz", self.DEFAULT_TIMEZONE)

    def function(self, source, *call_args):
        value = call_args[0]
        if isinstance(value, int):
            date = datetime.utcfromtimestamp(value)
        elif isinstance(value, basestring):
            date = parse_date(value)
        else:
            raise TypeError("Could not parse %s" % value)

        if date.tzinfo is None:
            date = date.replace(tzinfo=self.tz)

        return date
