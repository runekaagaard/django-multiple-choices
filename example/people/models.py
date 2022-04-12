from django.db import models
from multiple_choices import MultipleChoiceModelField

LIKES = ((0, "Pizza"), (1, "Juice"), (2, "Beef"), (3, "Orange juice"), (4, "Milk"))

class Person(models.Model):
    likes = MultipleChoiceModelField(choices=LIKES)

    def xfull_clean(self, exclude=None, validate_unique=True):
        return
        return super().full_clean(exclude=exclude, validate_unique=validate_unique)
