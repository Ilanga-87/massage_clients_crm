from datetime import datetime, timedelta

from django.http import HttpResponseRedirect
from django.views.generic import (TemplateView, ListView, CreateView, DetailView, FormView, UpdateView)
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.db.models import Min, F, Q, Value, ExpressionWrapper, DateTimeField, CharField
from django.db.models.functions import Concat, Cast

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
    template_name = 'clients_data/clients_list.html'  # Specify the template name explicitly

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(visit_client__visit_date__icontains=search_query) |
                Q(visit_client__visit_time__icontains=search_query) |
                Q(age__icontains=search_query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        closest_visits = (
            Visit.objects
            .annotate(closest_visit_datetime=ExpressionWrapper(Concat(
                F('visit_date'), Value(' '), F('visit_time'),
            ),
                output_field=DateTimeField()))
            .values('client_id')
            .annotate(closest_visit=Min('closest_visit_datetime'))
        )

        closest_visit_dict = {
            visit['client_id']: visit['closest_visit']
            for visit in closest_visits}
        context['closest_visits'] = closest_visit_dict

        ordering = self.request.GET.get('ordering')  # Get the ordering parameter from the request
        if ordering == 'name':
            context['object_list'] = self.model.objects.order_by('name')
        elif ordering == 'closest_visit':
            closest_visits = (
                Visit.objects
                .annotate(closest_visit_datetime=Cast(
                    Concat(F('visit_date'), Value(' '), Cast(F('visit_time'), output_field=CharField())),
                    output_field=DateTimeField()
                ))
                .values('client_id')
                .annotate(closest_visit=Min('closest_visit_datetime'))
                .order_by('closest_visit')
            )

            client_ids = [visit['client_id'] for visit in closest_visits]
            context['object_list'] = self.model.objects.filter(pk__in=client_ids)

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
                                                 visit_time__lt=time_range[i + 1])
                else:
                    visit = Visit.objects.filter(visit_date=dates[j], visit_time__gte=time_range[i])
                if len(visit) > 0:
                    for item in visit:
                        row[j + 1] = item
            timetable_matrix.append(row)

        context['dates'] = dates
        context['time_range'] = time_range
        context['timetable'] = timetable_matrix
        context['weekend'] = [5, 6]

        return context


class CompletedVisitsListView(ListView):
    model = Visit
    template_name = 'clients_data/completed_visits.html'
    context_object_name = 'completed_visits'

    def get_queryset(self):
        queryset = super().get_queryset()
        completed_visits = self.model.objects.filter(done_and_paid=True)

        search_query = self.request.GET.get('search')

        if search_query:
            completed_visits = completed_visits.filter(
                Q(client__name__icontains=search_query) |
                Q(massage_type__icontains=search_query) |
                Q(visit_date__icontains=search_query) |
                Q(client__age__icontains=search_query) |
                Q(visit_time__icontains=search_query) |
                Q(visit_price__icontains=search_query)
            ).distinct()
        return completed_visits

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordering = self.request.GET.get('ordering')  # Get the ordering parameter from the request

        if ordering == 'visit_date':
            context['object_list'] = self.model.objects.filter(done_and_paid=True).order_by('visit_date')
        elif ordering == 'massage_type':
            context['object_list'] = self.model.objects.filter(done_and_paid=True).order_by('massage_type')
        elif ordering == 'visit_price':
            context['object_list'] = self.model.objects.filter(done_and_paid=True).order_by('visit_price')
        elif ordering == 'name':
            context['object_list'] = self.model.objects.filter(done_and_paid=True).order_by('client__name')

        return context
