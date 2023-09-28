# Generated by Django 4.2.1 on 2023-07-23 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients_data', '0009_alter_visit_visit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='massage_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='visit',
            name='visit_price',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('pay_amount', models.PositiveIntegerField(blank=True, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_client', to='clients_data.client')),
            ],
        ),
    ]
