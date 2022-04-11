from django.test import TestCase
from multiple_choices import MultipleChoiceModelField, NullEncounteredError

class PeopleTestCase(TestCase):
    def setUp(self):
        self.m = MultipleChoiceModelField(choices=((1, "Foo"), (2, "Bar"), (3, "Baz")))

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
        self.assertEqual(self.m.get_prep_value(set([])), 0)
        self.assertEqual(self.m.get_prep_value(set([1, 2, 3])), 14)
        self.assertEqual(self.m.get_prep_value(set([1, 2])), 6)
