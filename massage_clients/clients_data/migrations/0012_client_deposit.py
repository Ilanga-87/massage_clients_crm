# Generated by Django 4.2.1 on 2023-07-24 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients_data', '0011_client_debt'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='deposit',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
