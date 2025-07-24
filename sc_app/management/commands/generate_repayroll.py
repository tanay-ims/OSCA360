# management/commands/generate_repayroll.py
from django.core.management.base import BaseCommand
from models import SeniorCitizen, Barangay, BenefitType, BenefitDisbursement, MilestoneBenefit, MissedPayout
from utils.pdf_generator import generate_masterlist_pdf
from django.conf import settings
from datetime import date
import os
from dateutil import rrule
from dateutil.parser import parse

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='Year for repayroll', default=date.today().year - 1)
        parser.add_argument('--start-month', type=int, help='Start month for birthday/milestone repayroll (1-12)')
        parser.add_argument('--end-month', type=int, help='End month for birthday/milestone repayroll (1-12)')
        parser.add_argument('--quarter', type=int, help='Quarter for local pension repayroll (1-4)')

    def handle(self, *args, **kwargs):
        year = kwargs['year']
        start_month = kwargs.get('start_month')
        end_month = kwargs.get('end_month')
        quarter = kwargs.get('quarter')
        today = date.today()

        if start_month and end_month and not (1 <= start_month <= 12 and 1 <= end_month <= 12):
            raise ValueError("Months must be between 1 and 12.")
        if quarter and not (1 <= quarter <= 4):
            raise ValueError("Quarter must be between 1 and 4.")

        for barangay in Barangay.objects.all():
            psgc = barangay.psgc_code
            seniors_data = {}

            # Birthday and milestone repayroll
            if start_month and end_month:
                birthday_cash = BenefitType.objects.get(name="BIRTHDAY_CASH")
                month_range = list(rrule.rrule(
                    rrule.MONTHLY,
                    dtstart=parse(f"{year}-{start_month}-01"),
                    until=parse(f"{year}-{end_month}-01")
                ))

                for month_dt in month_range:
                    month = month_dt.month
                    seniors_data[month] = []

                    # Birthday
                    missed_birthdays = MissedPayout.objects.filter(
                        barangay=barangay,
                        benefit_type=birthday_cash,
                        year=year,
                        month=month
                    )
                    for missed in missed_birthdays:
                        senior = missed.senior_citizen
                        if senior.status == 'A' and not BenefitDisbursement.objects.filter(
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
                                payroll_reference=f"repayroll-{psgc}-{month:02d}-{year}",
                                is_repayroll=True,
                                remarks=f"Repayroll for missed {month:02d}/{year} birthday"
                            )
                            seniors_data[month].append((senior.osca_id, senior.name))
                            missed.delete()

                    # Milestone
                    missed_milestones = MissedPayout.objects.filter(
                        barangay=barangay,
                        milestone_age__in=['80', '85', '90', '95', '100'],
                        year=year,
                        month=month
                    )
                    for missed in missed_milestones:
                        senior = missed.senior_citizen
                        if senior.status == 'A' and not MilestoneBenefit.objects.filter(
                            senior_citizen=senior,
                            milestone_age=missed.milestone_age
                        ).exists() and not BenefitDisbursement.objects.filter(
                            senior_citizen=senior,
                            benefit_type__name='BIRTHDAY_CASH',
                            disbursement_date__year=year
                        ).exists():
                            MilestoneBenefit.objects.create(
                                senior_citizen=senior,
                                milestone_age=missed.milestone_age,
                                amount=1000.00,  # Default, adjust if fixed
                                disbursement_date=today,
                                payroll_reference=f"repayroll-{milestone_age}-{psgc}-{month:02d}-{year}",
                                is_repayroll=True,
                                remarks=f"Repayroll for missed age {missed.milestone_age} in {month:02d}/{year}"
                            )
                            seniors_data[month].append((senior.osca_id, senior.name))
                            missed.delete()

                    # Generate PDF for each month
                    if seniors_data[month]:
                        period = f"Month {month:02d}-{year} (Repayroll)"
                        filename = os.path.join(
                            settings.MEDIA_ROOT,
                            f"payroll_masterlists/{psgc}/repayroll#1-{psgc}-{month:02d}-{year}.pdf"
                        )
                        generate_masterlist_pdf(barangay, period, seniors_data[month], "Birthday/Milestone Repayroll", filename)

            # Local pension repayroll
            if quarter:
                seniors_data[quarter] = []
                local_pension = BenefitType.objects.get(name="LOCAL_PENSION")
                missed_pensions = MissedPayout.objects.filter(
                    barangay=barangay,
                    benefit_type=local_pension,
                    year=year,
                    quarter=quarter
                )
                for missed in missed_pensions:
                    senior = missed.senior_citizen
                    if senior.status == 'A' and not BenefitDisbursement.objects.filter(
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
                            payroll_reference=f"repayroll-{psgc}-Q{quarter}-{year}",
                            is_repayroll=True,
                            remarks=f"Repayroll for missed Q{quarter} {year} pension"
                        )
                        seniors_data[quarter].append((senior.osca_id, senior.name))
                        missed.delete()

                # Generate PDF
                if seniors_data[quarter]:
                    period = f"Q{quarter}-{year} (Repayroll)"
                    filename = os.path.join(
                        settings.MEDIA_ROOT,
                        f"payroll_masterlists/{psgc}/repayroll-{psgc}-Q{quarter}-{year}.pdf"
                    )
                    generate_masterlist_pdf(barangay, period, seniors_data[quarter], "Local Pension Repayroll", filename)

        self.stdout.write(self.style.SUCCESS(f"Repayroll completed for {year}."))