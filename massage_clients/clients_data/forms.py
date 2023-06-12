from django import forms
from django.forms import inlineformset_factory
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
        fields = ('visit_date', 'visit_time', 'massage_type', 'visit_price', 'more_info')

        labels = {
            'visit_date': 'Дата приёма',
            'visit_time': 'Время приёма',
            'massage_type': 'Тип массажа',
            'visit_price': 'Цена приёма',
            'more_info': 'Детали'
        }

        widgets = {
            'visit_date': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd.MM.yyyy'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time', 'placeholder': 'hh:mm'}),
            'more_info': forms.Textarea(attrs={'rows': 2, 'cols': 4})
        }


VisitFormSet = inlineformset_factory(Client, Visit, form=VisitForm, extra=10)
