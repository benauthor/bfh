# -*- coding: utf-8 -*-
from unittest import TestCase

from bfh import Schema
from bfh.exceptions import Invalid
from bfh.fields import (
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
