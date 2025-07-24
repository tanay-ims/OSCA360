#models/group.py
from django.db import models

# Contains the Group model
class Group(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
