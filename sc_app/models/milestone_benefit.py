# models/milestone_benefit.py
from django.db import models
from django.core.exceptions import ValidationError
from .senior_citizen import SeniorCitizen
from .benefit_disbursement import BenefitDisbursement
from datetime import date

class MilestoneBenefit(models.Model):
    MILESTONE_AGES = (
        ('80', 'Age 80'),
        ('85', 'Age 85'),
        ('90', 'Age 90'),
        ('95', 'Age 95'),
        ('100', 'Age 100'),
    )
    senior_citizen = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='milestone_benefits'
    )
    milestone_age = models.CharField(max_length=3, choices=MILESTONE_AGES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    disbursement_date = models.DateField()
    payroll_reference = models.CharField(max_length=50, blank=True)
    is_repayroll = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    def clean(self):
        # Validate milestone age
        age = self.senior_citizen.get_age()
        disbursement_year = self.disbursement_date.year
        if age - (date.today().year - disbursement_year) != int(self.milestone_age):
            raise ValidationError(f"Senior's age does not match {self.milestone_age} in {disbursement_year}.")

        # Prevent duplicate milestone benefit
        if MilestoneBenefit.objects.filter(
            senior_citizen=self.senior_citizen,
            milestone_age=self.milestone_age
        ).exists():
            raise ValidationError(f"Milestone benefit for age {self.milestone_age} already disbursed.")

        # Prevent birthday cash gift in the same year
        if BenefitDisbursement.objects.filter(
            senior_citizen=self.senior_citizen,
            benefit_type__name='BIRTHDAY_CASH',
            disbursement_date__year=self.disbursement_date.year
        ).exists():
            raise ValidationError("Cannot disburse milestone benefit and birthday cash gift in the same year.")

        # Enforce payroll reference format
        if self.payroll_reference:
            psgc = self.senior_citizen.barangay.psgc_code
            year = str(self.disbursement_date.year)
            prefix = 'repayroll' if self.is_repayroll else 'Regular'
            if self.benefit_type.payroll_schedule == 'MONTHLY':
                month = self.disbursement_date.strftime('%m')
                expected = f"{prefix}-{milestone_age}-{psgc}-{month}-{year}"
            elif self.benefit_type.payroll_schedule == 'QUARTERLY':
                quarter = (self.disbursement_date.month - 1) // 3 + 1
                expected = f"{prefix}-{milestone_age}-{psgc}-Q{quarter}-{year}"
            else:
                expected = ''
            if self.payroll_reference != expected:
                raise ValidationError(f"Payroll reference must be {expected}.")

        # Restrict to active seniors
        if self.senior_citizen.status in ('D', 'T'):
            raise ValidationError("Cannot disburse milestone benefits to deceased or transferred seniors.")

    def __str__(self):
        return f"Milestone {self.milestone_age} to {self.senior_citizen.osca_id} on {self.disbursement_date}"

    class Meta:
        verbose_name_plural = "Milestone Benefits"
        unique_together = ('senior_citizen', 'milestone_age')
        indexes = [models.Index(fields=['disbursement_date', 'milestone_age'])]