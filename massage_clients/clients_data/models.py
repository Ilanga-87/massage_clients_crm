from django.db import models
from django.shortcuts import reverse


class Client(models.Model):
    GENDER_CHOICES = [
        ('М', 'Мужской'),
        ('Ж', 'Женский'),
    ]

    name = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    another_contact = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(blank=True, null=True)
    illnesses = models.TextField(blank=True)
    more_info = models.TextField(blank=True)
    balance = models.PositiveIntegerField(default=0, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('single_client', kwargs={'pk': self.pk, 'name': self.name})


class Visit(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='visit_client')
    visit_date = models.DateField()
    visit_time = models.TimeField()
    massage_type = models.CharField(max_length=100, blank=True)
    visit_price = models.PositiveIntegerField(null=True, blank=True)
    prepayment = models.PositiveIntegerField(null=True, blank=True, default=0)
    more_info = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    def get_closest_to(self, target):
        closest_greater_qs = self.filter(visit_date__gte=target).order_by('visit_date')

        try:
            closest_greater = closest_greater_qs[0]

        except IndexError:
            raise self.model.DoesNotExist("There is no closest object"
                                          " because there are no objects.")
        return closest_greater
