from django.db import models
from django.db.models import Lookup, Field

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

@Field.register_lookup
class In(Lookup):
    lookup_name = 'mcin'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

@Field.register_lookup
class NotIn(Lookup):
    lookup_name = 'mcnotin'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

@Field.register_lookup
class Equal(Lookup):
    lookup_name = 'mceq'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

@Field.register_lookup
class NotEqual(Lookup):
    lookup_name = 'mcneq'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params
