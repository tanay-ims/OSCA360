# models/signatory.py
from django.db import models


class Signatory(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    

    def __str__(self):
        return f"{self.name} ({self.title})"

    class Meta:
        verbose_name_plural = "Signatories"