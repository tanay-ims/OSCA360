# management/commands/tag_missed_payouts.py
from django.core.management.base import BaseCommand
from models import SeniorCitizen, Barangay, BenefitType, Eligibility, BenefitDisbursement, MilestoneBenefit, MissedPayout
from datetime import date
from dateutil import rrule
from dateutil.parser import parse

class Command(BaseCommand):
    help = 'Tag seniors who missed payouts for birthday, milestone, or local pension benefits.'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='Year for missed payouts', default=date.today().year - 1)
        parser.add_argument('--start-month', type=int, help='Start month for birthday/milestone (1-12)')
        parser.add_argument('--end-month', type=int, help='End month for birthday/milestone (1-12)')
        parser.add_argument('--quarter', type=int, help='Quarter for local pension (1-4)')

    def handle(self, *args, **kwargs):
        year = kwargs['year']
        start_month = kwargs.get('start_month')
        end_month = kwargs.get('end_month')
        quarter = kwargs.get('quarter')
        milestone_ages = {'80': 80, '85': 85, '90': 90, '95': 95, '100': 100}

        if start_month and end_month and not (1 <= start_month <= 12 and 1 <= end_month <= 12):
            raise ValueError("Months must be between 1 and 12.")
        if quarter and not (1 <= quarter <= 4):
            raise ValueError("Quarter must be between 1 and 4.")

        for barangay in Barangay.objects.all():
            psgc = barangay.psgc_code

            # Birthday and milestone tagging
            if start_month and end_month:
                birthday_cash = BenefitType.objects.get(name="BIRTHDAY_CASH")
                month_range = list(rrule.rrule(
                    rrule.MONTHLY,
                    dtstart=parse(f"{year}-{start_month}-01"),
                    until=parse(f"{year}-{end_month}-01")
                ))

                for month_dt in month_range:
                    month = month_dt.month
                    seniors = SeniorCitizen.objects.filter(
                        status='A',
                        barangay=barangay,
                        date_of_birth__month=month
                    )

                    # Birthday tagging
                    for senior in seniors:
                        if not BenefitDisbursement.objects.filter(
                            senior_citizen=senior,
                            benefit_type=birthday_cash,
                            disbursement_date__year=year
                        ).exists() and not MilestoneBenefit.objects.filter(
                            senior_citizen=senior,
                            disbursement_date__year=year
                        ).exists() and not MissedPayout.objects.filter(
                            senior_citizen=senior,
                            benefit_type=birthday_cash,
                            year=year,
                            month=month
                        ).exists():
                            MissedPayout.objects.create(
                                senior_citizen=senior,
                                benefit_type=birthday_cash,
                                barangay=barangay,
                                year=year,
                                month=month,
                                remarks=f"Missed birthday cash gift for {month_dt.strftime('%b')} {year}"
                            )

                    # Milestone tagging
                    for senior in seniors:
                        age = senior.get_age()
                        for milestone_age, target_age in milestone_ages.items():
                            milestone_year = year - (age - target_age)
                            if milestone_year == year and not MilestoneBenefit.objects.filter(
                                senior_citizen=senior,
                                milestone_age=milestone_age
                            ).exists() and not BenefitDisbursement.objects.filter(
                                senior_citizen=senior,
                                benefit_type__name='BIRTHDAY_CASH',
                                disbursement_date__year=year
                            ).exists() and not MissedPayout.objects.filter(
                                senior_citizen=senior,
                                milestone_age=milestone_age,
                                year=year,
                                month=month
                            ).exists():
                                MissedPayout.objects.create(
                                    senior_citizen=senior,
                                    milestone_age=milestone_age,
                                    barangay=barangay,
                                    year=year,
                                    month=month,
                                    remarks=f"Missed milestone age {milestone_age} in {month_dt.strftime('%b')} {year}"
                                )

            # Local pension tagging
            if quarter:
                local_pension = BenefitType.objects.get(name="LOCAL_PENSION")
                eligible_seniors = SeniorCitizen.objects.filter(
                    eligibilities__benefit_type=local_pension,
                    eligibilities__is_eligible=True,
                    status='A',
                    barangay=barangay
                )
                for senior in eligible_seniors:
                    if not BenefitDisbursement.objects.filter(
                        senior_citizen=senior,
                        benefit_type=local_pension,
                        disbursement_date__year=year,
                        disbursement_date__month__in=range((quarter-1)*3+1, quarter*3+1)
                    ).exists() and not MissedPayout.objects.filter(
                        senior_citizen=senior,
                        benefit_type=local_pension,
                        year=year,
                        quarter=quarter
                    ).exists():
                        MissedPayout.objects.create(
                            senior_citizen=senior,
                            benefit_type=local_pension,
                            barangay=barangay,
                            year=year,
                            quarter=quarter,
                            remarks=f"Missed local pension for Q{quarter} {year}"
                        )

        self.stdout.write(self.style.SUCCESS(f"Tagged missed payouts for {year}."))