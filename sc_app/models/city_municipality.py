from django.db import models
from django.core.validators import RegexValidator
from sc_app.models.province import Province  # <- Use explicit import, not wildcard

class CityMunicipality(models.Model):
    psgc_code = models.CharField(
        max_length=9,
        unique=True,
        validators=[RegexValidator(r'^\d{9}$', 'PSGC code must be a 9-digit number.')],
        help_text="9-digit PSGC code (e.g., 012801000 for Adams)"
    )
    name = models.CharField(max_length=100, help_text="City/Municipality name (e.g., Adams)")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities_municipalities')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.psgc_code})"

    class Meta:
        ordering = ['name']
        verbose_name = "City_Municipality"
        verbose_name_plural = "CitiesMunicipalities"