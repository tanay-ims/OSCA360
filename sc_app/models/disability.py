from django.db import models
from django.utils import timezone


# Disability Model
class Disability(models.Model):
    code = models.CharField(max_length=2, unique=True, help_text="Unique code for disability (e.g., VIS for Visual Impairment)")
    name = models.CharField(max_length=100, unique=True, help_text="Disability name (e.g., Visual Impairment, Mobility Impairment)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['code']