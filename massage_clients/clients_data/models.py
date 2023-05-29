from django.db import models
from django.shortcuts import reverse


class Client(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    another_contact = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(blank=True)
    illnesses = models.TextField(blank=True)
    massage_type = models.CharField(max_length=100)
    therapy_duration = models.PositiveIntegerField(blank=True, default=1)
    one_visit_price = models.PositiveIntegerField(blank=True, null=True)
    visit_days = models.CharField(max_length=100)
    visit_time = models.TimeField()
    more_info = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('single_client', kwargs={'pk': self.pk, 'name': self.name})
