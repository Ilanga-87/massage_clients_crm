# Generated by Django 4.2.1 on 2023-07-19 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('another_contact', models.CharField(blank=True, max_length=100)),
                ('sex', models.CharField(choices=[('М', 'Мужской'), ('Ж', 'Женский')], max_length=1)),
                ('age', models.PositiveIntegerField(blank=True, null=True)),
                ('illnesses', models.TextField(blank=True)),
                ('more_info', models.TextField(blank=True)),
                ('balance', models.PositiveIntegerField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_date', models.DateField()),
                ('visit_time', models.TimeField()),
                ('massage_type', models.CharField(max_length=100)),
                ('visit_price', models.PositiveIntegerField(default=0)),
                ('prepayment', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('more_info', models.TextField(blank=True)),
                ('completed', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visit_client', to='clients_data_per_visit.client')),
            ],
        ),
    ]
