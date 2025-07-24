# management/commands/generate_payroll.py
from django.core.management.base import BaseCommand
from models import SeniorCitizen, Barangay, BenefitType, BenefitDisbursement, MilestoneBenefit
from utils.pdf_generator import generate_masterlist_pdf
from django.conf import settings
from datetime import date
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        today = date.today()
        year = today.year
        month = today.strftime('%m')
        birthday_cash = BenefitType.objects.get(name="BIRTHDAY_CASH")
        milestone_ages = {'80': 80, '85': 85, '90': 90, '95': 95, '100': 100}

        for barangay in Barangay.objects.all():
            seniors = SeniorCitizen.objects.filter(status='A', barangay=barangay, date_of_birth__month=today.month)
            psgc = barangay.psgc_code
            seniors_data = []

            # Birthday payroll
            for senior in seniors:
                if not BenefitDisbursement.objects.filter(
                    senior_citizen=senior,
                    benefit_type=birthday_cash,
                    disbursement_date__year=year
                ).exists() and not MilestoneBenefit.objects.filter(
                    senior_citizen=senior,
                    disbursement_date__year=year
                ).exists():
                    BenefitDisbursement.objects.create(
                        senior_citizen=senior,
                        benefit_type=birthday_cash,
                        amount=birthday_cash.fixed_amount,
                        disbursement_date=today,
                        payroll_reference=f"Regular-{psgc}-{month}-{year}",
                        remarks=f"Birthday gift for {year}"
                    )
                    seniors_data.append((senior.osca_id, senior.name))

            # Milestone payroll
            for senior in seniors:
                age = senior.get_age()
                for milestone_age, target_age in milestone_ages.items():
                    if age == target_age and not MilestoneBenefit.objects.filter(
                        senior_citizen=senior,
                        milestone_age=milestone_age
                    ).exists() and not BenefitDisbursement.objects.filter(
                        senior_citizen=senior,
                        benefit_type__name='BIRTHDAY_CASH',
                        disbursement_date__year=year
                    ).exists():
                        MilestoneBenefit.objects.create(
                            senior_citizen=senior,
                            milestone_age=milestone_age,
                            amount=1000.00,  # Default, adjust if fixed
                            disbursement_date=today,
                            payroll_reference=f"Regular-{milestone_age}-{psgc}-{month}-{year}",
                            remarks=f"Milestone age {milestone_age} gift"
                        )
                        seniors_data.append((senior.osca_id, senior.name))

            # Generate PDF
            if seniors_data:
                period = f"Month {month}-{year}"
                filename = os.path.join(
                    settings.MEDIA_ROOT,
                    f"payroll_masterlists/{psgc}/Regular-{psgc}-{month}-{year}.pdf"
                )
                generate_masterlist_pdf(barangay, period, seniors_data, "Birthday/Milestone", filename)

        self.stdout.write(self.style.SUCCESS(f"Birthday and milestone payroll generated for {today.strftime('%b %Y')}."))