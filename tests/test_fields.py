# -*- coding: utf-8 -*-
from unittest import TestCase

from bfh.exceptions import Invalid
from bfh.fields import (
    IntegerField,
    UnicodeField,
    ArrayField,
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
