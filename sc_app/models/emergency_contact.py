from django.db import models
from django.utils import timezone
from sc_app.models.region import Region
from sc_app.models.province import Province
from sc_app.models.city_municipality import CityMunicipality
from sc_app.models.barangay import Barangay
from sc_app.models.relationship import Relationship


# Updated EmergencyContact Model
class EmergencyContact(models.Model):
    name = models.CharField(max_length=200, help_text="Full name of emergency contact")
    contact_number = models.CharField(max_length=15, blank=True)
    relationship = models.ForeignKey(Relationship, on_delete=models.SET_NULL, null=True, help_text="Relationship to senior citizen")
    address = models.TextField()
    barangay = models.ForeignKey(Barangay, on_delete=models.SET_NULL, null=True, help_text="Barangay of emergency contact")
    city_municipality = models.ForeignKey(CityMunicipality, on_delete=models.SET_NULL, null=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.relationship.name if self.relationship else 'No Relationship'})"
