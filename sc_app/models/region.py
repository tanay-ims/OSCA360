from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Region(models.Model):
    psgc_code = models.CharField(
        max_length=9,
        unique=True,
        validators=[RegexValidator(r'^\d{9}$', 'PSGC code must be a 9-digit number.')],
        help_text="9-digit PSGC code (e.g., 010000000 for Region I)"
    )
    name = models.CharField(max_length=100, help_text="Region name (e.g., Region I - Ilocos Region)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.psgc_code})"

    class Meta:
        ordering = ['name']