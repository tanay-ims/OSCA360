from django.db import models
from django.utils import timezone



# New Relationship Model
class Relationship(models.Model):
    code = models.CharField(max_length=2, unique=True, help_text="Unique code (e.g., 1 for Father, 2 for Mother)")
    name = models.CharField(max_length=30, unique=True, help_text="Relationship type (e.g., Father, Mother)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['code']