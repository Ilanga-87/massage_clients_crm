from datetime import datetime, timedelta

from django.http import HttpResponseRedirect
from django.views.generic import (TemplateView, ListView, CreateView, DetailView, FormView, UpdateView)
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.db.models import Min, F

from .forms import ClientForm, VisitFormSet
from .models import Client, Visit


class CreateClientView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients_data/create_client.html"


class SingleClientDisplayView(DetailView):
    model = Client


class AllClientsView(ListView):
    model = Client

    def get_context_data(self, **kwargs):
        context = super(AllClientsView, self).get_context_data(**kwargs)
        closest_visits = (
            Visit.objects
            .values('client_id')
            .annotate(closest_visit=Min('visit_date'))
        )
        closest_visit_dict = {visit['client_id']: visit['closest_visit'] for visit in closest_visits}
        context['closest_visits'] = closest_visit_dict

        # Order the clients based on closest visit date, with clients without a closest visit date appearing at the end
        context['object_list'] = self.model.objects.annotate(
            has_closest_visit=Min('visit_client__visit_date')
        ).order_by(F('has_closest_visit').asc(nulls_last=True))
        return context


class ClientVisitsEditView(SingleObjectMixin, FormView):
    model = Client
    template_name = 'clients_data/client_visits_edit.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Client.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Client.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        formset = VisitFormSet(**self.get_form_kwargs(), instance=self.object)
        formset.queryset = formset.queryset.exclude(done_and_paid=True)
        return formset

    def form_valid(self, form):
        formset = form

        if formset.is_valid():
            total_price = 0
            for visit_form in formset:
                if not visit_form.cleaned_data.get('DELETE', False):
                    visit_price = visit_form.cleaned_data.get('visit_price', 0)
                    done_and_paid = visit_form.cleaned_data.get('done_and_paid', False)

                    if done_and_paid:
                        total_price += visit_price

            self.object.balance += total_price
            self.object.save()

        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('single_client', kwargs={'pk': self.object.pk, 'name': self.object.name})


class SingleClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name_suffix = "_update_form"


class ScheduleView(TemplateView):
    template_name = 'clients_data/schedule_table_ex.html'


class TimetableView(TemplateView):
    template_name = 'clients_data/schedule_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get today's date and calculate the next 9 dates
        today = datetime.today().date()
        dates = [today + timedelta(days=i) for i in range(10)]

        # Define the time range from 13:00 to 21:00
        start_time = datetime.strptime("13:00", "%H:%M").time()
        end_time = datetime.strptime("21:00", "%H:%M").time()
        time_range = []
        current_time = start_time
        while current_time <= end_time:
            time_range.append(current_time)
            current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=60)).time()

        timetable_matrix = []

        for i in range(len(time_range)):
            row = [None] * (len(dates) + 1)
            row[0] = time_range[i]
            for j in range(len(dates)):
                if time_range[i] != time_range[-1]:
                    visit = Visit.objects.filter(visit_date=dates[j], visit_time__gte=time_range[i],
                                                 visit_time__lt=time_range[i+1])
                else:
                    visit = Visit.objects.filter(visit_date=dates[j], visit_time__gte=time_range[i])
                if len(visit) > 0:
                    for item in visit:
                        row[j+1] = item
            timetable_matrix.append(row)

        context['dates'] = dates
        context['time_range'] = time_range
        context['timetable'] = timetable_matrix

        return context


class CompletedVisitsListView(ListView):
    model = Visit
    template_name = 'clients_data/completed_visits.html'
    context_object_name = 'completed_visits'

    def get_queryset(self):
        return self.model.objects.filter(done_and_paid=True)
