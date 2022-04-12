# https://github.com/runekaagaard/django-multiple-choices
from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.db.models import Lookup, Field

class NullEncounteredError(Exception):
    pass

class MultipleChoicesWidget(forms.Select):
    allow_multiple_selected = True

    def render(self, /, *, name, value, attrs, **kwargs):
        if value is None:
            value = set()
        else:
            value = set(int(x) for x in value)

        def items(attrs):
            for k, v in attrs.items():
                if type(v) is bool:
                    yield k, k if v else ""
                else:
                    yield k, v

        attrs["multiple"] = True
        attrs["name"] = name
        attrs_str = " ".join(f'{k}="{str(v)}"' for k, v in items(attrs))
        html = [f"<select {attrs_str}>"]
        for choice in self.choices:
            selected = " selected" if (value and choice[0] in value) else ""
            html.append(f'<option value="{choice[0]}"{selected}>{choice[1]}</option>')

        html.append("</select>")

        return "".join(html)

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get

        return {int(x) for x in getter(name)}

    def value_omitted_from_data(self, data, files, name):
        # An unselected <select multiple> doesn't appear in POST data, so it's
        # never known if the value is actually omitted.
        return False

class MultipleChoicesFormField(forms.MultipleChoiceField):
    widget = MultipleChoicesWidget

    def __init__(self, *, coerce=None, **kwargs):
        kwargs.pop('empty_value', None)
        self.empty_value = set()
        super().__init__(**kwargs)
        self.choices = [x for x in self.choices if x[0] != ""]
        self.ns = set(int(x[0]) for x in self.choices)

    def to_python(self, value):
        if not value:
            return set()
        elif not isinstance(value, set):
            raise ValidationError(self.error_messages['invalid_list'], code='invalid_list')
        return {int(x) for x in value}

    def clean(self, value):
        value = super().clean(value)
        for choice in value:
            if choice not in self.ns:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': choice},
                )
        return value

    def validate(self, value):
        if value != self.empty_value:
            super().validate(value)
        elif self.required:
            raise ValidationError(self.error_messages['required'], code='required')

class MultipleChoicesModelField(models.PositiveBigIntegerField):
    def __init__(self, *args, **kwargs):
        self.required = kwargs.pop("required")
        kwargs["default"] = set()
        super(MultipleChoicesModelField, self).__init__(*args, **kwargs)
        self.ns = set(int(x[0]) for x in self.choices)
        assert sum(2**n for n in self.ns) <= 9223372036854775807, "To many choices. Sry!"

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
        elif isinstance(value, (set, list)):
            return value
        else:
            return self.from_db_value(value, 0, 0)

    def get_prep_value(self, value):
        assert type(value) is set, "The value of a MultipleChoicesModelField is always of type set."
        return sum(2**x for x in value)

    def formfield(self, **kwargs):
        defaults = {'choices_form_class': MultipleChoicesFormField, 'required': self.required}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def clean(self, value, instance):
        assert type(value) is set
        for n in value:
            if n not in self.ns:
                raise ValidationError("Invalid value {}".format(n))

        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['required'] = self.required
        return name, path, args, kwargs

@Field.register_lookup
class In(Lookup):
    lookup_name = 'mc_in'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s & %s != 0' % (lhs, rhs), params

@Field.register_lookup
class NotIn(Lookup):
    lookup_name = 'mc_notin'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s & %s == 0' % (lhs, rhs), params
