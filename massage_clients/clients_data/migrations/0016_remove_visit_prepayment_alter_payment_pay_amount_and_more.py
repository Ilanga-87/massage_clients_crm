# Generated by Django 4.2.1 on 2023-09-04 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients_data', '0015_alter_payment_options_remove_client_debt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visit',
            name='prepayment',
        ),
        migrations.AlterField(
            model_name='payment',
            name='pay_amount',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_date',
            field=models.DateField(),
        ),
    ]