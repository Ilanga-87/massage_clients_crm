from django import forms
from django.forms import inlineformset_factory
from django.utils import formats

from .models import Client, Visit


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'phone_number', 'another_contact', 'sex', 'age', 'illnesses', 'more_info')

        labels = {
            'name': 'Имя',
            'phone_number': 'Номер телефона',
            'another_contact': 'Доп. контакт',
            'sex': 'Пол',
            'age': 'Возраст',
            'illnesses': 'Жалобы и заболевания',
            'more_info': 'Детали',
        }

        widgets = {
            'illnesses': forms.Textarea(attrs={'rows': 3, 'cols': 4}),
            'more_info': forms.Textarea(attrs={'rows': 3, 'cols': 4}),
        }


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ('visit_date', 'visit_time', 'massage_type', 'visit_price', 'prepayment', 'more_info', 'completed')

        labels = {
            'visit_date': 'Дата приёма',
            'visit_time': 'Время приёма',
            'massage_type': 'Тип массажа',
            'visit_price': 'Цена приёма',
            'prepayment': 'Внесённая предоплата',
            'more_info': 'Детали',
            'completed': 'Проведен',
        }

        widgets = {
            'visit_date': forms.DateInput(
                attrs={'type': 'date', }),
            'visit_time': forms.TimeInput(attrs={'type': 'time',}),
            'more_info': forms.Textarea(attrs={'rows': 2, 'cols': 4}),
            'visit_price': forms.NumberInput(attrs={'step': 100})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            visit_date = self.instance.visit_date
            self.initial['visit_date'] = formats.date_format(visit_date, 'Y-m-d')


VisitFormSet = inlineformset_factory(Client, Visit, form=VisitForm, extra=10)
