# models/benefit_type.py
from django.db import models

class BenefitType(models.Model):
    BENEFIT_TYPES = (
        ('BD_CG', 'Birthday Cash Gift'),
        ('LGU_SP', 'Local Social Pension'),
        ('NGA_SP', 'National Social Pension'),
        ('OT_MB', 'Other Local Monetary Benefit'),
    )
    PAYROLL_SCHEDULES = (
        ('NONE', 'None'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    )
    name = models.CharField(max_length=6, choices=BENEFIT_TYPES, unique=True)
    description = models.TextField(blank=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    requires_eligibility = models.BooleanField(default=False)
    payroll_schedule = models.CharField(max_length=20, choices=PAYROLL_SCHEDULES, default='NONE')

    def __str__(self):
        return self.get_name_display()