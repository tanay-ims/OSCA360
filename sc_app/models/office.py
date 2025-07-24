# 1. models/office.py
# Contains the Office model
from django.db import models

class Office(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name