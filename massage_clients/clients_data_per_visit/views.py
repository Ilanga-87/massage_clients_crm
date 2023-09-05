from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import (TemplateView, ListView, CreateView, DetailView, FormView, UpdateView, DeleteView)
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Min, F, Q, Value, ExpressionWrapper, DateTimeField, CharField, Sum
from django.db.models.functions import Concat, Cast, ExtractYear, ExtractMonth
from django.contrib.auth.mixins import PermissionRequiredMixin

from .forms import ClientForm, VisitFormSet
from .models import Client, Visit
from . import service_data


class RedirectPermissionRequiredMixin(PermissionRequiredMixin):
    login_url = reverse_lazy('home')

    def handle_no_permission(self):
        return redirect(self.get_login_url())


class CreateClientView(RedirectPermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients_data_per_visit/create_client.html"

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')


class SingleClientDisplayView(RedirectPermissionRequiredMixin, DetailView):
    model = Client

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object()
        future_visits = object.visit_client.filter(done_and_paid=False)
        context['future_visits'] = future_visits
        remaining_payments = future_visits.aggregate(remaining_payments_sum=Sum('visit_price'))['remaining_payments_sum']

        context['remaining_payments'] = remaining_payments
        return context


class AllClientsView(RedirectPermissionRequiredMixin, ListView):
    model = Client
    template_name = 'clients_data_per_visit/clients_list.html'

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')

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
        search_query = self.request.GET.get('search')

        # Calculate the closest visit for each client for context data
        closest_visits = (
            Visit.objects
            .annotate(closest_visit_datetime=ExpressionWrapper(Concat(
                F('visit_date'), Value(' '), F('visit_time'),
            ),
                output_field=DateTimeField()))
            .values('client_id')
            .annotate(closest_visit=Min('closest_visit_datetime'))
            .order_by('closest_visit')
        )

        all_clients = Client.objects.all()

        # Create a dictionary to map client IDs to their closest visit dates
        closest_visit_dict = {
            visit['client_id']: visit['closest_visit']
            for visit in closest_visits}

        context['closest_visits'] = closest_visit_dict

        if search_query:
            ordering = self.request.GET.get('ordering', 'closest_visit')  # Get the ordering parameter from the request
            closest_visits = closest_visits.filter(
                Q(client__name__icontains=search_query) |
                Q(client__phone_number__icontains=search_query) |
                Q(visit_date__icontains=search_query) |
                Q(visit_time__icontains=search_query) |
                Q(client__age__icontains=search_query)
            ).distinct()

            # Create a set of client IDs that match the filtered closest_visits
            matching_client_ids = set(visit['client_id'] for visit in closest_visits)

            # Create a dictionary to map client IDs to their closest visit dates
            closest_visit_dict = {
                visit['client_id']: visit['closest_visit']
                for visit in closest_visits}
            # Filter the clients that have matching IDs
            clients_to_display = [
                client for client in all_clients if client.id in matching_client_ids
            ]
            context['closest_visits'] = closest_visit_dict

            if ordering == 'name':
                context['object_list'] = sorted(clients_to_display, key=lambda client: client.name)
            else:
                # Sort the clients based on their closest visit dates
                sentinel_datetime = datetime(9999, 12, 31, tzinfo=timezone.utc)
                sorted_clients = sorted(
                    clients_to_display,
                    key=lambda client: closest_visit_dict.get(client.id, sentinel_datetime)
                )

                context['object_list'] = sorted_clients

        else:
            ordering = self.request.GET.get('ordering', 'closest_visit')  # Get the ordering parameter from the request
            if ordering == 'name':
                context['object_list'] = self.model.objects.order_by('name')
            else:
                # Sort the clients based on their closest visit dates
                sentinel_datetime = datetime(9999, 12, 31, tzinfo=timezone.utc)
                sorted_clients = sorted(
                    all_clients,
                    key=lambda client: closest_visit_dict.get(client.id, sentinel_datetime)
                )

                context['object_list'] = sorted_clients

        return context


class ClientVisitsEditView(RedirectPermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Client
    template_name = 'clients_data_per_visit/client_visits_edit.html'

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')

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
        return reverse('single_client_pv', kwargs={'pk': self.object.pk, 'name': self.object.name})


class SingleClientUpdateView(RedirectPermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name_suffix = "_update_form"

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')


class SingleClientDeleteView(RedirectPermissionRequiredMixin, DeleteView):
    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    model = Client
    context_object_name = 'client'
    success_url = reverse_lazy('clients_list_pv')

    def form_valid(self, form):
        return super(SingleClientDeleteView, self).form_valid(form)


class TimetableView(RedirectPermissionRequiredMixin, TemplateView):
    template_name = 'clients_data_per_visit/schedule_table.html'

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')

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


class CompletedVisitsListView(RedirectPermissionRequiredMixin, ListView):
    model = Visit
    template_name = 'clients_data_per_visit/completed_visits.html'
    context_object_name = 'completed_visits'

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')

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
        search_query = self.request.GET.get('search')

        if search_query:
            completed_visits = self.model.objects.filter(done_and_paid=True).filter(
                Q(client__name__icontains=search_query) |
                Q(massage_type__icontains=search_query) |
                Q(visit_date__icontains=search_query) |
                Q(client__age__icontains=search_query) |
                Q(visit_time__icontains=search_query) |
                Q(visit_price__icontains=search_query)
            ).distinct()

            if ordering == 'visit_date':
                completed_visits = completed_visits.order_by('visit_date')
                visits_by_month = {}

                for visit in completed_visits:
                    month = service_data.months_dict[visit.visit_date.strftime('%B')]
                    if month in visits_by_month:
                        visits_by_month[month].append(visit)
                    else:
                        visits_by_month[month] = [visit]

                context['visits_by_month'] = visits_by_month
            elif ordering == 'massage_type':
                completed_visits = completed_visits.order_by('massage_type')
            elif ordering == 'visit_price':
                completed_visits = completed_visits.order_by('visit_price')
            elif ordering == 'name':
                completed_visits = completed_visits.order_by('client__name')
                visits_by_letter = {}
                for visit in completed_visits:
                    first_letter = visit.client.name[0].upper()
                    if first_letter.isalpha():
                        if first_letter in visits_by_letter:
                            visits_by_letter[first_letter].append(visit)
                        else:
                            visits_by_letter[first_letter] = [visit]

                context['visits_by_letter'] = visits_by_letter

            context['object_list'] = completed_visits
        else:
            completed_visits = self.model.objects.filter(done_and_paid=True)
            if ordering == 'visit_date':
                completed_visits = completed_visits.order_by('visit_date')
                visits_by_month = {}

                for visit in completed_visits:
                    month = service_data.months_dict[visit.visit_date.strftime('%B')]
                    if month in visits_by_month:
                        visits_by_month[month].append(visit)
                    else:
                        visits_by_month[month] = [visit]

                context['visits_by_month'] = visits_by_month

            elif ordering == 'massage_type':
                completed_visits = completed_visits.order_by('massage_type')
            elif ordering == 'visit_price':
                completed_visits = completed_visits.order_by('visit_price')
            elif ordering == 'name':
                completed_visits = completed_visits.order_by('client__name')
                visits_by_letter = {}
                for visit in completed_visits:
                    first_letter = visit.client.name[0].upper()
                    if first_letter.isalpha():
                        if first_letter in visits_by_letter:
                            visits_by_letter[first_letter].append(visit)
                        else:
                            visits_by_letter[first_letter] = [visit]

                context['visits_by_letter'] = visits_by_letter

            context['object_list'] = completed_visits

        return context


class ActualVisitsListView(RedirectPermissionRequiredMixin, ListView):
    model = Visit
    template_name = 'clients_data_per_visit/actual_visits.html'
    context_object_name = 'actual_visits'

    permission_required = ('clients_data_per_visit.view_client',
                           'clients_data_per_visit.add_client',
                           'clients_data_per_visit.change_client',
                           'clients_data_per_visit.delete_client')

    def get_queryset(self):
        queryset = super().get_queryset()
        actual_visits = self.model.objects.filter(done_and_paid=False)

        search_query = self.request.GET.get('search')

        if search_query:
            actual_visits = actual_visits.filter(
                Q(client__name__icontains=search_query) |
                Q(massage_type__icontains=search_query) |
                Q(visit_date__icontains=search_query) |
                Q(client__age__icontains=search_query) |
                Q(visit_time__icontains=search_query) |
                Q(visit_price__icontains=search_query)
            ).distinct()

        return actual_visits

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordering = self.request.GET.get('ordering')  # Get the ordering parameter from the request
        search_query = self.request.GET.get('search')

        if search_query:
            actual_visits = self.model.objects.filter(done_and_paid=False).filter(
                Q(client__name__icontains=search_query) |
                Q(massage_type__icontains=search_query) |
                Q(visit_date__icontains=search_query) |
                Q(client__age__icontains=search_query) |
                Q(visit_time__icontains=search_query) |
                Q(visit_price__icontains=search_query)
            ).distinct()

            if ordering == 'visit_date':
                actual_visits = actual_visits.order_by('visit_date')
                visits_by_month = {}

                for visit in actual_visits:
                    month = service_data.months_dict[visit.visit_date.strftime('%B')]
                    if month in visits_by_month:
                        visits_by_month[month].append(visit)
                    else:
                        visits_by_month[month] = [visit]

                context['visits_by_month'] = visits_by_month
            elif ordering == 'massage_type':
                actual_visits = actual_visits.order_by('massage_type')
            elif ordering == 'visit_price':
                actual_visits = actual_visits.order_by('visit_price')
            elif ordering == 'name':
                actual_visits = actual_visits.order_by('client__name')
                visits_by_letter = {}
                for visit in actual_visits:
                    first_letter = visit.client.name[0].upper()
                    if first_letter.isalpha():
                        if first_letter in visits_by_letter:
                            visits_by_letter[first_letter].append(visit)
                        else:
                            visits_by_letter[first_letter] = [visit]

                context['visits_by_letter'] = visits_by_letter

            context['object_list'] = actual_visits
        else:
            actual_visits = self.model.objects.filter(done_and_paid=False)
            if ordering == 'visit_date':
                actual_visits = actual_visits.order_by('visit_date')
                visits_by_month = {}

                for visit in actual_visits:
                    month = service_data.months_dict[visit.visit_date.strftime('%B')]
                    if month in visits_by_month:
                        visits_by_month[month].append(visit)
                    else:
                        visits_by_month[month] = [visit]

                context['visits_by_month'] = visits_by_month
            elif ordering == 'massage_type':
                actual_visits = actual_visits.order_by('massage_type')
            elif ordering == 'visit_price':
                actual_visits = actual_visits.order_by('visit_price')
            elif ordering == 'name':
                actual_visits = actual_visits.order_by('client__name')
                visits_by_letter = {}
                for visit in actual_visits:
                    first_letter = visit.client.name[0].upper()
                    if first_letter.isalpha():
                        if first_letter in visits_by_letter:
                            visits_by_letter[first_letter].append(visit)
                        else:
                            visits_by_letter[first_letter] = [visit]

                context['visits_by_letter'] = visits_by_letter

            context['object_list'] = actual_visits

        return context


# Charts views


@staff_member_required
def get_filter_options(request):
    # Get distinct year
    grouped_payments = Visit.objects.annotate(year=ExtractYear("visit_date")).values("year").order_by("-year") \
        .distinct()
    options = [payment["year"] for payment in grouped_payments]

    # Get distinct client names
    client_names = Client.objects.values_list("name", flat=True).distinct()

    return JsonResponse({
        "options": options,
        "client_names": list(client_names),
    })


@staff_member_required
def get_balance_chart(request, period):
    client_name = request.GET.get("client")
    visits = Visit.objects.all()

    if period == "last_3_months":
        # Calculate the date range for the last 3 months
        end_date = timezone.now()
        start_date = end_date - relativedelta(months=3)
    elif period == "last_6_months":
        # Calculate the date range for the last 6 months
        end_date = timezone.now()
        start_date = end_date - relativedelta(months=6)
    elif period == "last_year":
        # Calculate the date range for the last year (12 months)
        end_date = timezone.now()
        start_date = end_date - relativedelta(months=12)
    else:
        # Year option selected, calculate date range accordingly
        start_date = timezone.make_aware(datetime(year=int(period), month=1, day=1))
        end_date = timezone.make_aware(
            datetime(year=int(period), month=12, day=31, hour=23, minute=59, second=59))

    visits = visits.filter(visit_date__range=[start_date, end_date])

    if client_name:
        visits = visits.filter(client__name=client_name)

    grouped_visits = visits.annotate(price=F("visit_price")).annotate(month=ExtractMonth("visit_date")) \
        .values("month").annotate(average=Sum("visit_price")).values("month", "average").order_by("month")

    visits_dict = service_data.get_year_dict()

    for group in grouped_visits:
        visits_dict[service_data.months_list[group["month"] - 1]] = round(group["average"], 2)

    # Calculate total_sum
    total_sum = visits.aggregate(total_sum=Sum("visit_price"))["total_sum"] or 0

    return JsonResponse({
        "title": f"Payments in {period}",
        "data": {
            "labels": list(visits_dict.keys()),
            "datasets": [{
                "label": "Сумма (сом)",
                "backgroundColor": "#13C5DD",
                "borderColor": "#13C5DD",
                "data": list(visits_dict.values()),
            }]
        },
        "total_sum": total_sum,
    })


@staff_member_required
def statistics_view(request, client_name=None, period=None):
    return render(request, 'clients_data_per_visit/balance_chart.html', {})


