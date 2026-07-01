import random
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from employees.models import Department, Employee, Skill


class Command(BaseCommand):
    help = "Seed the database with sample data: 10 Departments, 100 Employees, and 20 Managers."

    DEPARTMENT_DATA = [
        ("Engineering", "Software development and engineering team."),
        ("Human Resources", "HR management and employee relations."),
        ("Finance", "Accounting, payroll, and financial planning."),
        ("Marketing", "Brand management, advertising, and growth."),
        ("Sales", "Business development and client acquisition."),
        ("Operations", "Day-to-day business operations management."),
        ("IT Support", "Technical support and infrastructure."),
        ("Legal", "Legal compliance and contract management."),
        ("Product", "Product strategy, design, and roadmap."),
        ("Customer Success", "Customer onboarding and retention."),
    ]

    SKILL_NAMES = [
        "Python", "Django", "JavaScript", "React", "PostgreSQL",
        "Docker", "AWS", "Git", "REST API", "Machine Learning",
        "Communication", "Leadership", "Project Management", "Agile",
        "Data Analysis", "SQL", "Linux", "CI/CD", "Testing", "DevOps",
    ]

    FIRST_NAMES = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun",
        "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
        "Ananya", "Diya", "Saanvi", "Aanya", "Aadhya",
        "Priya", "Meera", "Riya", "Neha", "Pooja",
    ]

    LAST_NAMES = [
        "Sharma", "Verma", "Gupta", "Singh", "Kumar",
        "Patel", "Reddy", "Nair", "Joshi", "Mehta",
    ]

    DESIGNATIONS = [
        "Software Engineer", "Senior Developer", "Team Lead",
        "Analyst", "Manager", "Associate", "Consultant",
        "Architect", "Intern", "Executive",
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting data seeding..."))

        # ── 1. Create Skills ──
        skills = []
        for skill_name in self.SKILL_NAMES:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills.append(skill)
            if created:
                self.stdout.write(f"  Created Skill: {skill_name}")

        # ── 2. Create Departments ──
        departments = []
        for name, desc in self.DEPARTMENT_DATA:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={"description": desc},
            )
            departments.append(dept)
            if created:
                self.stdout.write(f"  Created Department: {name}")

        self.stdout.write(self.style.SUCCESS(f"  [OK] {len(departments)} Departments ready."))

        # ── 3. Create 100 Employees ──
        existing_count = Employee.objects.count()
        employees_created = 0

        for i in range(1, 101):
            emp_id = f"EMP{existing_count + i:04d}"

            # Skip if already exists
            if Employee.objects.filter(employee_id=emp_id).exists():
                continue

            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}.{existing_count + i}@company.com"

            joining = date.today() - timedelta(days=random.randint(30, 1500))
            salary = Decimal(random.randint(25000, 200000))

            emp = Employee(
                employee_id=emp_id,
                first_name=first,
                last_name=last,
                email=email,
                phone=f"{random.randint(7000000000, 9999999999)}",
                salary=salary,
                joining_date=joining,
                designation=random.choice(self.DESIGNATIONS),
                department=random.choice(departments),
                status=random.choice([True, True, True, False]),  # 75% active
            )
            emp.save()

            # Assign 1-4 random skills
            emp.skills.set(random.sample(skills, k=random.randint(1, 4)))

            employees_created += 1

        self.stdout.write(self.style.SUCCESS(f"  [OK] {employees_created} Employees created."))

        # ── 4. Assign 20 Managers ──
        all_employees = list(Employee.objects.all())
        managers = random.sample(all_employees, min(20, len(all_employees)))
        manager_count = 0

        for emp in all_employees:
            if emp not in managers:
                emp.manager = random.choice(managers)
                # Use update to avoid triggering full_clean on seeded data
                Employee.objects.filter(pk=emp.pk).update(manager=emp.manager)
                manager_count += 1

        self.stdout.write(self.style.SUCCESS(f"  [OK] 20 Managers assigned to {manager_count} employees."))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete!"))
