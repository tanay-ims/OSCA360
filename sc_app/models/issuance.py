# models/issuance.py
from django.db import models
from sc_app.models.senior_citizen import SeniorCitizen
from sc_app.models.inventory import Inventory

class Issuance(models.Model):
    senior_citizen = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='issuances'
    )
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='issuances'
    )
    issuance_date = models.DateField()
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Issuance of {self.inventory.form_type} to {self.senior_citizen.osca_id} on {self.issuance_date}"

    class Meta:
        verbose_name_plural = "Issuances"
        unique_together = ('senior_citizen', 'inventory')  # Prevent duplicate issuances