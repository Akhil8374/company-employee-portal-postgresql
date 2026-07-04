import random
from decimal import Decimal
from datetime import date, timedelta, time

from django.core.management.base import BaseCommand
from django.db import transaction

from employees.models import Employee, Department, Skill, Attendance


class Command(BaseCommand):
    help = "Generate a large dataset for performance testing."

    TARGET_EMPLOYEES = 5000
    TARGET_ATTENDANCE = 50000

    FIRST_NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna","Ishaan","Ananya","Diya","Saanvi","Aanya","Aadhya","Priya","Meera","Riya","Neha","Pooja"]
    LAST_NAMES = ["Sharma","Verma","Gupta","Singh","Kumar","Patel","Reddy","Nair","Joshi","Mehta"]
    DESIGNATIONS = ["Software Engineer","Senior Developer","Team Lead","Analyst","Manager","Associate","Consultant","Architect","Executive"]

    @transaction.atomic
    def handle(self, *args, **options):
        departments = list(Department.objects.all())
        skills = list(Skill.objects.all())

        if not departments:
            self.stdout.write(self.style.ERROR("Run seed_data first."))
            return

        current = Employee.objects.count()

        for i in range(current + 1, self.TARGET_EMPLOYEES + 1):
            emp = Employee.objects.create(
                employee_id=f"EMP{i:05}",
                first_name=random.choice(self.FIRST_NAMES),
                last_name=random.choice(self.LAST_NAMES),
                email=f"user{i}@company.com",
                phone=str(random.randint(7000000000,9999999999)),
                salary=Decimal(random.randint(25000,200000)),
                joining_date=date.today()-timedelta(days=random.randint(1,1800)),
                designation=random.choice(self.DESIGNATIONS),
                department=random.choice(departments),
                status=random.choice([True,True,True,False]),
            )
            if skills:
                emp.skills.set(random.sample(skills, min(random.randint(1,4), len(skills))))

        employees = list(Employee.objects.all())
        attendance = []

        while len(attendance) < self.TARGET_ATTENDANCE:
            emp = random.choice(employees)
            attendance.append(
                Attendance(
                    employee=emp,
                    date=date.today()-timedelta(days=random.randint(0,365*5)),
                    status=random.choice(["PRESENT","ABSENT","LEAVE","HALF_DAY"]),
                    check_in=time(9,0),
                    check_out=time(18,0),
                )
            )
            if len(attendance) == 1000:
                Attendance.objects.bulk_create(
                    attendance,
                    batch_size=1000,
                    ignore_conflicts=True,
                )
                attendance = []

        if attendance:
            Attendance.objects.bulk_create(
                attendance,
                batch_size=1000,
                ignore_conflicts=True,
            )

        self.stdout.write(self.style.SUCCESS("Large dataset generation complete."))
