from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from sc_app.models.region import Region



class Province(models.Model):
    psgc_code = models.CharField(
        max_length=9,
        unique=True,
        validators=[RegexValidator(r'^\d{9}$', 'PSGC code must be a 9-digit number.')],
        help_text="9-digit PSGC code (e.g., 012800000 for Ilocos Norte)"
    )
    name = models.CharField(max_length=100, help_text="Province name (e.g., Ilocos Norte)")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='provinces')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.psgc_code})"

    class Meta:
        ordering = ['name']