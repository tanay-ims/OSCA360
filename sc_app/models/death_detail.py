# models/death_detail.py
from django.db import models
from sc_app.models.senior_citizen import SeniorCitizen

class DeathDetail(models.Model):
    senior_citizen = models.OneToOneField(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='death_detail',
    )
    date_of_death = models.DateField()
    cause_of_death = models.CharField(max_length=200, blank=True)
    certificate_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Death detail for {self.senior_citizen.name}"