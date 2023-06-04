from django import forms
from django.forms import formset_factory, inlineformset_factory
from .models import Client, Visit


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('is_archived', )

        labels = {
            'name': 'Name',
            'phone_number': 'Phone Number',
            'another_contact': 'Another Contact',
            'sex': 'Sex',
            'age': 'Age',
            'illnesses': 'Illnesses',
            'massage_type': 'Massage Type',
            'therapy_duration': 'Therapy Duration',
            'one_visit_price': 'One Visit Price',
            'first_visit_date': 'First Visit Date',
            'first_visit_time': 'First Visit Time',
            'more_info': 'More Information',
        }

        widgets = {
            'illnesses': forms.Textarea(attrs={'rows': 5, 'cols': 4}),
            'more_info': forms.Textarea(attrs={'rows': 4, 'cols': 4}),
            'first_visit_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'dd.MM.yyyy (DOB)', 'class': 'form-control'}),
            'first_visit_time': forms.TimeInput(attrs={'type': 'time', 'placeholder': 'hh:mm', 'class': 'form-control'})
        }


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ('client', 'visit_date', 'visit_time')

        labels = {
            'visit_date': 'Visit Date',
            'visit_time': 'Visit Time',
        }

        widgets = {
            'visit_date': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd.MM.yyyy (DOB)', 'class': 'form-control'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time', 'placeholder': 'hh:mm', 'class': 'form-control'})
        }


VisitFormSet = inlineformset_factory(Client, Visit, form=VisitForm, extra=1,)
