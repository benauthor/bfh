from __future__ import absolute_import

NULLISH = (None, {}, [], tuple())


def nullish(value, implicit_nulls=True):
    if implicit_nulls:
        if hasattr(value, 'is_empty'):
            return value.is_empty

        return value in NULLISH

    return value is None
