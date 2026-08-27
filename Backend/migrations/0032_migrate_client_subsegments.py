from django.db import migrations


def migrate_client_subsegments(apps, schema_editor):

    Client = apps.get_model('Backend', 'Client')
    MarketingSubsegment = apps.get_model(
        'Backend',
        'marketing_subsegment'
    )

    subsegments = {
        subsegment.name: subsegment
        for subsegment in MarketingSubsegment.objects.all()
    }

    updated = 0
    not_found = []

    for client in Client.objects.all():

        if not client.subsegment_label:
            continue

        marketing_subsegment = subsegments.get(
            client.subsegment_label
        )

        if marketing_subsegment:

            client.subsegment = marketing_subsegment
            client.save(
                update_fields=['subsegment']
            )

            updated += 1

        else:

            not_found.append(
                f'{client.name} -> {client.subsegment_label}'
            )

    print(f'\nClientes actualizados: {updated}')

    if not_found:

        print('\nSubsegmentos no encontrados:')

        for item in not_found:
            print(item)


def reverse_migration(apps, schema_editor):

    Client = apps.get_model('Backend', 'Client')

    for client in Client.objects.all():

        if client.subsegment:

            client.subsegment_label = client.subsegment.name

            client.save(
                update_fields=['subsegment_label']
            )


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0031_client_subsegment'),
    ]

    operations = [

        migrations.RunPython(
            migrate_client_subsegments,
            reverse_migration
        )

    ]