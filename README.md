# django-multiple-choices

Alternative to https://github.com/disqus/django-bitfield and https://github.com/goinnn/django-multiselectfield/ that:

- Works on MySQL (postgres not tested)
- Stores the selected value as a bitmask value which allows for fast filtering.

# Usage

Import it and stick it on a model:

```
from django.db import models
from multiple_choices import MultipleChoicesModelField

LIKES = ((0, "Pizza"), (1, "Juice"), (2, "Beef"), (3, "Orange juice"), (4, "Milk"))

class Person(models.Model):
    likes = MultipleChoicesModelField(choices=LIKES, required=True)
```

Both the `choices` and the `required` props are required.

Two new filters are available:

```
Person.objects.filter(likes__mc__in={0, 1}) # Persons who like pizza and juice
Person.objects.filter(likes__mc__notin={4}) # Persons who doesn't like milk
Persons.objects.filter(likes={2}) # Persons who likes beef and nothing else.
```

# Installation

Copy ´multiple_choices.py` somewhere on your python path.
