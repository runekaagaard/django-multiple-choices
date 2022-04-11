from django.db import models

class NullEncounteredError(Exception):
    pass

class MultipleChoiceModelField(models.PositiveBigIntegerField):
    def __init__(self, *args, **kwargs):
        super(MultipleChoiceModelField, self).__init__(*args, **kwargs)
        self.ns = set(int(x[0]) for x in self.choices)

    def from_db_value(self, value, expression, connection):
        if value is None:
            raise NullEncounteredError("NULL is not supported, use 0 as default value.")

        value = int(value)
        if value == 0:
            return set()
        else:
            return set(n for n in self.ns if value & (2**n))

    def to_python(self, value):
        if value is None:
            raise NullEncounteredError("None is not supported, use 0/set() as default value.")
        elif isinstance(value, set):
            return value
        else:
            return self.from_db_value(value, 0, 0)

    def get_prep_value(self, value):
        assert type(value) is set, "The value of a MultipleChoiceModelField is always of type set."
        return sum(2**x for x in value)
