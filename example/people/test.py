d = dict
from django.core.exceptions import ValidationError
from django.test import TestCase
from django import forms
from multiple_choices import MultipleChoiceModelField, NullEncounteredError
from people.models import Person

class PersonModelForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = []

class MultipleChoiceModelFieldTestCase(TestCase):
    def setUp(self):
        self.m = MultipleChoiceModelField(choices=((1, "Foo"), (2, "Bar"), (3, "Baz")))

    def test_init(self):
        with self.assertRaises(AssertionError):
            MultipleChoiceModelField(choices=((x, "") for x in range(64)))

    def test_from_db_value(self):
        with self.assertRaises(NullEncounteredError):
            self.m.from_db_value(None, 0, 0)
        self.assertEqual(self.m.from_db_value(0, 0, 0), set())
        self.assertEqual(self.m.from_db_value(14, 0, 0), set([1, 2, 3]))
        self.assertEqual(self.m.from_db_value("14", 0, 0), set([1, 2, 3]))

    def test_to_python(self):
        with self.assertRaises(NullEncounteredError):
            self.m.to_python(None)
        self.assertEqual(self.m.to_python(14), set([1, 2, 3]))
        self.assertEqual(self.m.to_python("14"), set([1, 2, 3]))
        self.assertEqual(self.m.to_python(12), set([2, 3]))
        self.assertEqual(self.m.to_python(set([1, 2, 3])), set([1, 2, 3]))

    def test_get_prep_value(self):
        with self.assertRaises(AssertionError):
            self.m.get_prep_value(None)
        self.assertEqual(self.m.get_prep_value(set([])), 0)
        self.assertEqual(self.m.get_prep_value(set([1, 2, 3])), 14)
        self.assertEqual(self.m.get_prep_value(set([1, 2])), 6)

    def test_form_field(self):
        html = str(PersonModelForm(instance=Person(likes={2, 3})))
        assert 'value="0">' in html
        assert 'value="1">' in html
        assert 'value="2" selected>' in html
        assert 'value="3" selected>' in html
        assert 'value="4">' in html

        f = PersonModelForm(data=d(likes={1, 2}))
        self.assertEqual(f.is_valid(), True)

        f = PersonModelForm(data=d(likes=set()))
        self.assertEqual(f.is_valid(), False)

        f = PersonModelForm(data=d(likes=set([999])))
        self.assertEqual(f.is_valid(), False)

    def test_model_field(self):
        p = Person(likes={1})
        p.likes.add(2)
        self.assertEqual(p.likes, {1, 2})
        p.likes.remove(2)
        self.assertEqual(p.likes, {1})

        with self.assertRaises(ValidationError):
            p.likes.add(999999999)
            p.full_clean()
