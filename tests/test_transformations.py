from unittest import TestCase

from bfh.exceptions import Missing
from bfh.transformations import (
    Bool,
    Concat,
    Do,
    Get,
    Int,
    Num,
    Str,
)


class TestGet(TestCase):
    def test_can_get_from_dict(self):
        my_dict = {"path": "goal"}
        result = Get("path")(my_dict)
        self.assertEqual(result, "goal")

    def test_can_nest(self):
        my_dict = {"path": {"subpath": "goal"}}
        result = Get("path", "subpath")(my_dict)
        self.assertEqual(result, "goal")

    def test_can_nest_deeply(self):
        my_dict = {"path": {"deep": {"deeper": {"deepest": "goal"}}}}
        result = Get("path", "deep", "deeper", "deepest")(my_dict)
        self.assertEqual(result, "goal")

    def test_can_get_from_obj(self):
        class MyObj(object):
            path = "goal"
        result = Get("path")(MyObj())
        self.assertEqual(result, "goal")

    def test_mandatory_raises(self):
        my_dict = {"path": "goal"}
        with self.assertRaises(Missing):
            Get("other")(my_dict)

    def test_optional_missing_is_none(self):
        my_dict = {"path": "goal"}
        result = Get("else", optional=True)(my_dict)
        self.assertIsNone(result)


class TestCoerce(TestCase):
    def test_can_coerce_int(self):
        my_int = 1
        result = Int(my_int)()
        self.assertEqual(my_int, result)
        result = Int(str(my_int))()
        self.assertEqual(my_int, result)
        result = Int(unicode(my_int))()
        self.assertEqual(my_int, result)
        result = Int(float(my_int))()
        self.assertEqual(my_int, result)

    def test_can_coerce_num(self):
        my_float = 1.01
        result = Num(my_float)()
        self.assertEqual(my_float, result)
        result = Num(int(my_float))()
        self.assertEqual(1.0, result)
        result = Num(unicode(my_float))()
        self.assertEqual(my_float, result)

    def test_can_coerce_unicode(self):
        my_str = u"1"
        result = Str(my_str)()
        self.assertEqual(my_str, result)
        result = Str(int(my_str))()
        self.assertEqual(my_str, result)
        result = Str(float(my_str))()
        self.assertEqual(u"1.0", result)

    def test_can_coerce_bool(self):
        result = Bool(True)()
        self.assertIs(True, result)
        result = Bool(1)()
        self.assertIs(True, result)
        result = Bool("wow")()
        self.assertIs(True, result)
        result = Bool(0)()
        self.assertIs(False, result)
        result = Bool(None)()
        self.assertIs(False, result)

    def test_can_nest_coercion(self):
        my_int = 1
        nested = Str(Bool(Num(my_int)))
        result = nested()
        self.assertEqual(result, u"True")


class TestConcat(TestCase):
    def test_can_concat(self):
        first = "one"
        second = "two"
        result = Concat(first, second)()
        self.assertEqual(first + second, result)

        third = "three"
        result = Concat(first, second, third)()
        self.assertEqual(first + second + third, result)

    def test_can_nest_concat(self):
        first = "one"
        second = "two"
        third = "three"
        result = Concat(first, Concat(second, third))()
        self.assertEqual(first + second + third, result)


class TestDo(TestCase):
    def test_can_do(self):
        start = "wow"
        transform = lambda a: a.upper()
        result = Do(transform, start)()
        self.assertEqual("WOW", result)

    def test_multiple_args(self):
        transform = lambda a, b, c: a + b + c
        result = Do(transform, 1, 2, 3)()
        self.assertEqual(6, result)


class TestMixedTransformations(TestCase):
    def test_can_mix_transformations(self):
        original = {"foo": 1, "bar": 2}
        concat_getter = Concat(Str(Get("foo")), ":", Str(Get("bar")))
        result = concat_getter(original)
        expected = u"1:2"
        self.assertEqual(expected, result)

        int_concatter = Int(Concat("1", Str(Get("bar")), "3"))
        result = int_concatter(original)
        self.assertEqual(123, result)
