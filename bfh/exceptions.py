class Invalid(TypeError):
    pass


class Missing(KeyError, AttributeError):
    pass
