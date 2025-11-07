# people/management/commands/import_people.py
import csv
from django.core.management.base import BaseCommand
from people.models import People, Department

class Command(BaseCommand):
    help = "Import people from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to CSV file")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["姓名"].strip()
                email = row["信箱"].strip()
                phone = row["電話"].strip() if row.get("電話") else None
                dept_name = row["部門"].strip() if row.get("部門") else None

                department = None
                if dept_name:
                    department, _ = Department.objects.get_or_create(name=dept_name)

                person, created = People.objects.get_or_create(
                    email=email,
                    defaults={
                        "name": name,
                        "phone": phone,
                        "department": department,
                    },
                )

                if not created:  # 如果人已存在，可以更新
                    person.name = name
                    person.phone = phone
                    person.department = department
                    person.save()

                self.stdout.write(self.style.SUCCESS(f"Imported: {person}"))
