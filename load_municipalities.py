import os
import django
import csv

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'FinantialEv_v1.settings'
)
django.setup()
from Backend.models import Department, Municipality
count = 0
with open(
    'municipalities.csv',
    encoding='utf-8-sig'
) as file:
    reader = csv.DictReader(file,delimiter=';')
    print(reader.fieldnames)
    for row in reader:
        try:
            dept = Department.objects.get(
                name=row['department'].strip()
            )
            Municipality.objects.get_or_create(
                dane=int(row['dane code']),
                defaults={
                    'name': row['municipality'].strip(),
                    'department': dept
                }
            )
            count += 1
        except Department.DoesNotExist:
            print(
                f"Department not found: "
                f"{row['department']}"
            )
print(f"{count} municipalities processed")
print("Task finished")