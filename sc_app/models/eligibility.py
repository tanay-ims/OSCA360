# models/eligibility.py
from django.db import models
from .senior_citizen import SeniorCitizen
from .benefit_type import BenefitType

class Eligibility(models.Model):
    senior_citizen = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='eligibilities'
    )
    benefit_type = models.ForeignKey(
        BenefitType,
        on_delete=models.CASCADE,
        related_name='eligibilities'
    )
    is_eligible = models.BooleanField(default=True)
    eligibility_date = models.DateField()
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.senior_citizen.osca_id} - {self.benefit_type} (Eligible: {self.is_eligible})"

    class Meta:
        unique_together = ('senior_citizen', 'benefit_type')