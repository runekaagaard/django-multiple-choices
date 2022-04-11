from django.db import models
from multiple_choices import MultipleChoiceModelField

LIKES = ((0, "Pizza"), (1, "Juice"), (2, "Beef"), (3, "Orange juice"), (4, "Milk"))

class Person(models.Model):
    likes = MultipleChoiceModelField(choices=LIKES)
