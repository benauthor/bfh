from __future__ import absolute_import


class Invalid(TypeError):
    pass


class Missing(KeyError, AttributeError):
    pass
