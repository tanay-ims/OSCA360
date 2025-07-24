from django.db import models
from django.utils import timezone



# Religion Model
class Religion(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="Unique code for religion (e.g., RC for Roman Catholic)")
    name = models.CharField(max_length=100, unique=True, help_text="Religion name (e.g., Roman Catholic)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['code']