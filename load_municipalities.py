import os
import django
import csv

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'FinantialEv_v1.settings'
)
django.setup()

from Backend.models import Municipality

count = 0

with open(
    'municipalities.csv',
    encoding='utf-8-sig'
) as file:

    reader = csv.DictReader(file, delimiter=';')
    print(reader.fieldnames)

    for row in reader:

        Municipality.objects.filter(
            dane=int(row['dane code'])
        ).update(
            latitude=float(row['latitude'].replace(',', '.')),
            longitude=float(row['longitude'].replace(',', '.')),
            node=row['node'].strip(),
            region=row['region'].strip()
        )

        count += 1

print(f"{count} municipalities updated")
print("Task finished")