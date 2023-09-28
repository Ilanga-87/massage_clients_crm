from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import formats

from .models import Client, Visit, Payment


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
        fields = ('visit_date', 'visit_time', 'massage_type', 'visit_price', 'more_info', 'completed')

        labels = {
            'visit_date': 'Дата приёма',
            'visit_time': 'Время приёма',
            'massage_type': 'Тип массажа',
            'visit_price': 'Цена приёма',
            'more_info': 'Детали',
            'completed': 'Проведен',
        }

        widgets = {
            'visit_date': forms.DateInput(
                attrs={'type': 'date', }),
            'visit_time': forms.TimeInput(attrs={'type': 'time', }),
            'more_info': forms.Textarea(attrs={'rows': 2, 'cols': 4}),
            'visit_price': forms.NumberInput(attrs={'step': 50})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            visit_date = self.instance.visit_date
            self.initial['visit_date'] = formats.date_format(visit_date, 'Y-m-d')


VisitFormSet = inlineformset_factory(Client, Visit, form=VisitForm, extra=10)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('payment_date', 'pay_amount')

        labels = {
            'payment_date': 'Дата выплаты',
            'pay_amount': 'Сумма выплаты',
        }

        widgets = {
            'payment_date': forms.DateInput(
                attrs={'type': 'date', }),
            'pay_amount': forms.NumberInput(attrs={'step': 50})
        }
