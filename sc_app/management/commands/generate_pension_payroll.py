# management/commands/generate_pension_payroll.py
from django.core.management.base import BaseCommand
from models import SeniorCitizen, Barangay, BenefitType, Eligibility, BenefitDisbursement
from utils.pdf_generator import generate_masterlist_pdf
from django.conf import settings
from datetime import date
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = date.today()
        year = today.year
        quarter = (today.month - 1) // 3 + 1
        local_pension = BenefitType.objects.get(name="LOCAL_PENSION")

        for barangay in Barangay.objects.all():
            eligible_seniors = SeniorCitizen.objects.filter(
                eligibilities__benefit_type=local_pension,
                eligibilities__is_eligible=True,
                status='A',
                barangay=barangay
            )
            psgc = barangay.psgc_code
            seniors_data = []

            for senior in eligible_seniors:
                if not BenefitDisbursement.objects.filter(
                    senior_citizen=senior,
                    benefit_type=local_pension,
                    disbursement_date__year=year,
                    disbursement_date__month__in=range((quarter-1)*3+1, quarter*3+1)
                ).exists():
                    BenefitDisbursement.objects.create(
                        senior_citizen=senior,
                        benefit_type=local_pension,
                        amount=local_pension.fixed_amount,
                        disbursement_date=today,
                        payroll_reference=f"Regular-{psgc}-Q{quarter}-{year}",
                        remarks=f"Q{quarter} {year} local pension"
                    )
                    seniors_data.append((senior.osca_id, senior.name))

            # Generate PDF
            if seniors_data:
                period = f"Q{quarter}-{year}"
                filename = os.path.join(
                    settings.MEDIA_ROOT,
                    f"payroll_masterlists/{psgc}/Regular-{psgc}-Q{quarter}-{year}.pdf"
                )
                generate_masterlist_pdf(barangay, period, seniors_data, "Local Pension", filename)

        self.stdout.write(self.style.SUCCESS(f"Local pension payroll generated for Q{quarter} {year}."))