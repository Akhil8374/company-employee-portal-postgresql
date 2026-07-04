import os
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from employees.models import Employee


class Command(BaseCommand):
    help = "Deactivate employees who have been inactive (not updated) for more than 180 days and generate a report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=180,
            help="Number of inactive days threshold (default: 180).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview which employees would be deactivated without making changes.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find employees who haven't been updated in over 'days' days
        inactive_employees = Employee.objects.filter(
            status=True,
            updated_at__lt=cutoff_date,
        )

        count = inactive_employees.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f"No employees found inactive for more than {days} days.")
            )
            return

        self.stdout.write(
            self.style.WARNING(f"Found {count} employees inactive for more than {days} days.")
        )

        # Generate report
        reports_dir = os.path.join(settings.BASE_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(reports_dir, f"deactivated_users_{timestamp}.txt")

        with open(filepath, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("DEACTIVATED USERS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Threshold: {days} days\n")
            f.write(f"Dry Run: {'Yes' if dry_run else 'No'}\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"{'Employee ID':<15} {'Name':<25} {'Last Updated':<20}\n")
            f.write("-" * 60 + "\n")

            for emp in inactive_employees:
                f.write(
                    f"{emp.employee_id:<15} "
                    f"{emp.first_name} {emp.last_name:<20} "
                    f"{emp.updated_at.strftime('%Y-%m-%d %H:%M'):<20}\n"
                )

            f.write(f"\nTotal: {count} employees\n")

        self.stdout.write(self.style.SUCCESS(f"  [OK] Report saved: {filepath}"))

        # Deactivate unless dry run
        if not dry_run:
            updated = inactive_employees.update(status=False)
            self.stdout.write(
                self.style.SUCCESS(f"  [OK] Deactivated {updated} employees.")
            )
        else:
            self.stdout.write(
                self.style.NOTICE("  ⏭ Dry run — no changes made.")
            )
