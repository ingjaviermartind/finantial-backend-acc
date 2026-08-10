import os
import django
import pandas as pd

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'FinantialEv_v1.settings'
)
django.setup()

from Backend.models import Client

count = 0

df = pd.read_excel(
    'clients.xlsx',
    sheet_name='to_db'
)

print(df.columns.tolist())

for _, row in df.iterrows():

    verification_number = (
        None
        if pd.isna(row['verification_number'])
        else int(row['verification_number'])
    )

    Client.objects.update_or_create(
        identification_number=int(row['identification_number']),
        defaults={
            'verification_number': verification_number,
            'name': str(row['name']).strip(),
            'subsegment': str(row['subsegment']).strip(),
        }
    )
    count += 1

print(f"{count} clients processed")
print("Task finished")