# models/transfer_detail.py
from django.db import models
from sc_app.models.senior_citizen import SeniorCitizen

class TransferDetail(models.Model):
    senior_citizen = models.OneToOneField(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='transfer_detail',
    )
    transfer_date = models.DateField()
    destination = models.CharField(max_length=200)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"Transfer detail for {self.senior_citizen.name}"