from django.db import migrations


def populate_region(apps, schema_editor):
    Municipality = apps.get_model('Backend', 'Municipality')
    Region = apps.get_model('Backend', 'Region')

    regions = {
        region.name: region.id
        for region in Region.objects.all()
    }

    for municipality in Municipality.objects.all():

        if municipality.region_name:
            region_id = regions.get(municipality.region_name)

            if region_id:
                municipality.region_id = region_id
                municipality.save(update_fields=['region'])


def reverse_region(apps, schema_editor):
    Municipality = apps.get_model('Backend', 'Municipality')

    for municipality in Municipality.objects.select_related('region'):
        if municipality.region:
            municipality.region_name = municipality.region.name
            municipality.save(update_fields=['region_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0022_municipality_region'),
    ]

    operations = [
        migrations.RunPython(
            populate_region,
            reverse_region
        ),
    ]