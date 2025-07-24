# models/benefit_disbursement.py
from django.db import models
from django.core.exceptions import ValidationError
from sc_app.models.senior_citizen import SeniorCitizen
from sc_app.models.benefit_type import BenefitType
from datetime import date

class BenefitDisbursement(models.Model):
    senior_citizen = models.ForeignKey(
        SeniorCitizen,
        on_delete=models.CASCADE,
        related_name='disbursements'
    )
    benefit_type = models.ForeignKey(
        BenefitType,
        on_delete=models.CASCADE,
        related_name='disbursements'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    disbursement_date = models.DateField()
    payroll_reference = models.CharField(max_length=50, blank=True)
    is_repayroll = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    def clean(self):
        # Enforce fixed amounts
        if self.benefit_type.fixed_amount and self.amount != self.benefit_type.fixed_amount:
            raise ValidationError(
                f"Amount for {self.benefit_type} must be {self.benefit_type.fixed_amount}."
            )

        # Check eligibility for pensions
        if self.benefit_type.requires_eligibility:
            eligibility = Eligibility.objects.filter(
                senior_citizen=self.senior_citizen,
                benefit_type=self.benefit_type,
                is_eligible=True
            ).exists()
            if not eligibility:
                raise ValidationError(f"{self.senior_citizen.osca_id} is not eligible for {self.benefit_type}.")

        # Prevent double pension benefits
        if self.benefit_type.name in ('LOCAL_PENSION', 'NATIONAL_PENSION'):
            other_pension = 'NATIONAL_PENSION' if self.benefit_type.name == 'LOCAL_PENSION' else 'LOCAL_PENSION'
            quarter = (self.disbursement_date.month - 1) // 3 + 1
            if BenefitDisbursement.objects.filter(
                senior_citizen=self.senior_citizen,
                benefit_type__name=other_pension,
                disbursement_date__year=self.disbursement_date.year,
                disbursement_date__month__in=range((quarter-1)*3+1, quarter*3+1)
            ).exists():
                raise ValidationError("Cannot disburse both local and national pensions in the same quarter.")

        # Prevent multiple birthday disbursements
        if self.benefit_type.name == 'BIRTHDAY_CASH':
            if BenefitDisbursement.objects.filter(
                senior_citizen=self.senior_citizen,
                benefit_type=self.benefit_type,
                disbursement_date__year=self.disbursement_date.year
            ).exists():
                raise ValidationError("Birthday cash gift already disbursed this year.")
            if MilestoneBenefit.objects.filter(
                senior_citizen=self.senior_citizen,
                disbursement_date__year=self.disbursement_date.year
            ).exists():
                raise ValidationError("Cannot disburse birthday cash gift with milestone in the same year.")

        # Enforce payroll reference format
        if self.payroll_reference:
            psgc = self.senior_citizen.barangay.psgc_code
            year = str(self.disbursement_date.year)
            prefix = 'repayroll' if self.is_repayroll else 'Regular'
            if self.benefit_type.payroll_schedule == 'MONTHLY':
                month = self.disbursement_date.strftime('%m')
                expected = f"{prefix}-{psgc}-{month}-{year}"
            elif self.benefit_type.payroll_schedule == 'QUARTERLY':
                quarter = (self.disbursement_date.month - 1) // 3 + 1
                expected = f"{prefix}-{psgc}-Q{quarter}-{year}"
            else:
                expected = ''
            if self.payroll_reference != expected:
                raise ValidationError(f"Payroll reference must be {expected}.")

        # Restrict to active seniors
        if self.senior_citizen.status in ('D', 'T'):
            raise ValidationError("Cannot disburse benefits to deceased or transferred seniors.")

    def __str__(self):
        return f"{self.benefit_type} to {self.senior_citizen.osca_id} on {self.disbursement_date}"

    class Meta:
        verbose_name_plural = "Benefit Disbursements"
        indexes = [models.Index(fields=['disbursement_date', 'benefit_type'])]