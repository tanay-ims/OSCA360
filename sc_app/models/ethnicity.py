from django.db import models
from django.utils import timezone


# Ethnicity Model
class Ethnicity(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="Unique code for ethnicity (e.g., TAG for Tagalog)")
    name = models.CharField(max_length=100, unique=True, help_text="Ethnicity name (e.g., Tagalog, Ilocano)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['code']