#models/designation.py
from django.db import models

# Contains the Designation model
class Designation(models.Model):
    class_id = models.CharField(max_length=10, unique=True)
    class_name = models.CharField(max_length=100)

    def __str__(self):
        return self.class_name