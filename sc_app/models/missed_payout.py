# models/missed_payout.py
from django.db import models
from .senior_citizen import SeniorCitizen
from .benefit_type import BenefitType
from .barangay import Barangay

class MissedPayout(models.Model):
    senior_citizen = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='missed_payouts'
    )
    benefit_type = models.ForeignKey(
        BenefitType,
        on_delete=models.CASCADE,
        related_name='missed_payouts',
        null=True,  # Null for milestone benefits
    )
    milestone_age = models.CharField(max_length=3, blank=True)  # For milestone benefits (80, 85, etc.)
    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.CASCADE,
        related_name='missed_payouts'
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(null=True, blank=True)  # For monthly benefits
    quarter = models.PositiveIntegerField(null=True, blank=True)  # For quarterly benefits
    tagged_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.benefit_type and self.benefit_type.name.startswith('MILESTONE'):
            raise ValidationError("Use milestone_age for milestone benefits, not benefit_type.")
        if self.milestone_age and not self.benefit_type:
            if self.milestone_age not in [age[0] for age in MilestoneBenefit.MILESTONE_AGES]:
                raise ValidationError(f"Invalid milestone_age: {self.milestone_age}.")
        if self.month and self.quarter:
            raise ValidationError("Cannot specify both month and quarter.")
        if self.benefit_type and self.benefit_type.payroll_schedule == 'MONTHLY' and not self.month:
            raise ValidationError("Month is required for monthly benefits.")
        if self.benefit_type and self.benefit_type.payroll_schedule == 'QUARTERLY' and not self.quarter:
            raise ValidationError("Quarter is required for quarterly benefits.")

    def __str__(self):
        period = f"Q{self.quarter}" if self.quarter else f"Month {self.month:02d}"
        benefit = self.benefit_type.name if self.benefit_type else f"Milestone {self.milestone_age}"
        return f"Missed {benefit} for {self.senior_citizen.osca_id} in {period} {self.year}"

    class Meta:
        verbose_name_plural = "Missed Payouts"
        unique_together = ('senior_citizen', 'benefit_type', 'milestone_age', 'year', 'month', 'quarter')
        indexes = [models.Index(fields=['year', 'month', 'quarter'])]