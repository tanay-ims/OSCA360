from django.db import models
from django.utils import timezone


# Education Model
class Education(models.Model):
    psec_code = models.CharField(
        max_length=5,
        unique=True,
        help_text="Philippine Standard Education Code (e.g., ELEM for Elementary)"
    )
    name = models.CharField(max_length=100, unique=True, help_text="Education level (e.g., Elementary, High School)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.psec_code})"

    class Meta:
        ordering = ['psec_code']