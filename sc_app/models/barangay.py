from django.db import models
from django.core.validators import RegexValidator
from sc_app.models.city_municipality import CityMunicipality

class Barangay(models.Model):
    psgc_code = models.CharField(
        max_length=9,
        unique=True,
        validators=[RegexValidator(r'^\d{9}$', 'PSGC code must be a 9-digit number.')],
        help_text="9-digit PSGC code (e.g., 012801001 for Adams Poblacion)"
    )
    name = models.CharField(max_length=100, help_text="Barangay name (e.g., Poblacion)")
    city_municipality = models.ForeignKey(CityMunicipality, on_delete=models.CASCADE, related_name='barangays')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.psgc_code})"

    class Meta:
        ordering = ['name']