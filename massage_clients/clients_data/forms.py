from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('is_archived',)

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
            'visit_days': 'Visit Days',
            'visit_time': 'Visit Time',
            'more_info': 'More Information',
        }

        widgets = {
            'myfield': forms.TextInput(attrs={'class': 'myfieldclass'}),
        }
