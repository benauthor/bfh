# -*- coding: utf-8 -*-
from unittest import TestCase

from bfh import Schema
from bfh.exceptions import Invalid
from bfh.fields import (
    DictField,
    IntegerField,
    UnicodeField,
    ArrayField,
    Subschema
)


class TestFieldValidation(TestCase):
    def test_int_validation(self):
        field = IntegerField()

        assert field.validate(1)

        with self.assertRaises(Invalid):
            field.validate("wow")

        with self.assertRaises(Invalid):
            field.validate(1.0)

        with self.assertRaises(Invalid):
            field.validate([])

        with self.assertRaises(Invalid):
            field.validate(None)

    def test_optional_validation(self):
        field = IntegerField(required=False)
        assert field.validate(None)

    def test_unicode_validation(self):
        field = UnicodeField()

        assert field.validate(u'wow ☃')

        assert field.validate('still ok')

        with self.assertRaises(Invalid):
            field.validate(1.0)

        with self.assertRaises(Invalid):
            field.validate(None)

        field = UnicodeField(required=False)

        assert field.validate(u'wow ☃')

        assert field.validate(None)

        with self.assertRaises(Invalid):
            field.validate(1)

        field = UnicodeField(strict=True)

        assert field.validate(u'nice snowman ☃')

        with self.assertRaises(Invalid):
            field.validate('not strict enough')

    def test_array_validation(self):
        field = ArrayField(int)

        assert field.validate([1, 2, 3])

        with self.assertRaises(Invalid):
            field.validate(["a", 1, 1.0])

        with self.assertRaises(Invalid):
            field.validate(None)

        with self.assertRaises(Invalid):
            field.validate({1: "A", 2: "B"})

        with self.assertRaises(Invalid):
            field.validate("hiya")

        field = ArrayField(int, required=False)

        assert field.validate([1, 2, 3])

        assert field.validate(None)

        with self.assertRaises(Invalid):
            field.validate(1)

    def test_dict_validation(self):
        field = DictField()

        assert field.validate({})

        assert field.validate({"foo": "bar"})

        with self.assertRaises(Invalid):
            field.validate(1)

        with self.assertRaises(Invalid):
            field.validate([])

        with self.assertRaises(Invalid):
            field.validate(None)

        class SomeSchema(Schema):
            inner = IntegerField()

        assert field.validate(SomeSchema(inner=1))

        with self.assertRaises(Invalid):
            field.validate(SomeSchema(inner="wow"))

        field = DictField(required=False)

        assert field.validate({"foo": "bar"})

        assert field.validate(None)


class TestFieldSerialization(TestCase):
    def test_array_serialization(self):
        field = ArrayField(int)
        flat = [1, 2, 3]
        self.assertEqual(flat, field.serialize(flat))

        empty = None
        self.assertEqual([], field.serialize(empty))

        class SomeSchema(Schema):
            wat = IntegerField()

        field = ArrayField(Subschema)
        source = [SomeSchema(wat=1), SomeSchema(wat=2)]
        self.assertEqual([{"wat": 1}, {"wat": 2}], field.serialize(source))

    def test_dict_serialization(self):
        field = DictField()
        source = {"wow": "cool"}
        self.assertEqual(source, field.serialize(source))

        class SomeSchema(Schema):
            great = ArrayField(int)

        source = SomeSchema(great=[1, 2, 3])
        self.assertEqual({"great": [1, 2, 3]}, field.serialize(source))
