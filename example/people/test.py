d = dict
from django.core.exceptions import ValidationError
from django.test import TestCase
from django import forms
from multiple_choices import MultipleChoicesModelField, NullEncounteredError
from people.models import Person

class PersonModelForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = []

class MultipleChoiceModelFieldTestCase(TestCase):
    def setUp(self):
        self.m = MultipleChoicesModelField(required=True, choices=((1, "Foo"), (2, "Bar"), (3, "Baz")))

    def test_init(self):
        with self.assertRaises(AssertionError):
            MultipleChoicesModelField(required=True, choices=((x, "") for x in range(64)))

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

    def test_lookups(self):
        Person.objects.create(likes={0, 2, 1})
        Person.objects.create(likes={1, 4, 2})
        Person.objects.create(likes={5, 4, 1, 2})
        Person.objects.create(likes={2, 3})
        self.assertEqual(Person.objects.count(), 4)
        self.assertEqual(Person.objects.filter(likes__mc_in={1}).count(), 3)
        self.assertEqual(Person.objects.filter(likes__mc_in={5}).count(), 1)
        self.assertEqual(Person.objects.filter(likes__mc_in={6}).count(), 0)
        self.assertEqual(Person.objects.filter(likes__mc_notin={5}).count(), 3)
        self.assertEqual(Person.objects.filter(likes__mc_notin={2}).count(), 0)

    def test_demo_doesnt_chrash(self):
        Person.objects.filter(likes__mc_in={0, 1})  # Persons who like pizza and juice
        Person.objects.filter(likes__mc_notin={4})  # Persons who doesn't like milk
        Person.objects.filter(likes={2})  # Persons who likes beef and nothing else.
