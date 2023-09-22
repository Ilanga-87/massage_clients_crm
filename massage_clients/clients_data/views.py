from datetime import datetime, date, timedelta

from dateutil.relativedelta import relativedelta
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.views.generic import (TemplateView, ListView, CreateView, DetailView, FormView, UpdateView, DeleteView)
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Min, F, Q, Value, ExpressionWrapper, DateTimeField, Sum
from django.db.models.functions import Concat
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse

from .forms import ClientForm, VisitFormSet, PaymentForm
from .models import Client, Visit, Payment
from . import service_data


class RedirectPermissionRequiredMixin(PermissionRequiredMixin):
    login_url = reverse_lazy('home')

    def handle_no_permission(self):
        return redirect(self.get_login_url())


class CreateClientView(RedirectPermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients_data/create_client.html"

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')


class SingleClientDisplayView(RedirectPermissionRequiredMixin, DetailView):
    model = Client

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object(queryset=Client.objects.all())
        query = Visit.objects.filter(completed=False).filter(client__pk=self.kwargs['pk'])

        paid_visits_cost = self.object.deposit
        unpaid_visits_cost = 0

        for visit in query:
            if visit.visit_price:
                unpaid_visits_cost += visit.visit_price
            else:
                unpaid_visits_cost += 0
        remaining_payments = (paid_visits_cost - unpaid_visits_cost) * -1
        context['remaining_payments'] = remaining_payments

        return context


class SingleClientCompletedVisits(RedirectPermissionRequiredMixin, ListView):
    model = Visit
    template_name = 'clients_data/client_detail_completed_visits.html'
    context_object_name = 'completed_visits'

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    def get_queryset(self):
        client_pk = self.kwargs['pk']
        client_name = self.kwargs['name']
        completed_visits = Visit.objects.filter(client__pk=client_pk, client__name=client_name, completed=True)

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

        pk = self.kwargs.get('pk')
        name = self.kwargs.get('name')
        client = get_object_or_404(Client, pk=pk, name=name)
        client_name = client.name

        context['client'] = client
        context['client_name'] = client_name

        completed_visits = self.get_queryset()
        context['object_list'] = completed_visits

        ordering = self.request.GET.get('ordering')  # Get the ordering parameter from the request
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

            context['object_list'] = completed_visits
            context['ordering'] = ordering
        else:
            completed_visits = completed_visits
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

            context['object_list'] = completed_visits
            context['ordering'] = ordering

        return context


class AllClientsView(RedirectPermissionRequiredMixin, ListView):
    model = Client
    template_name = 'clients_data/clients_list.html'

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

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
                object_list = sorted(clients_to_display, key=lambda client: client.name)
                clients_by_letters = {}
                for client in object_list:
                    first_letter = client.client.name[0].upper()
                    if first_letter.isalpha():
                        if first_letter in clients_by_letters:
                            clients_by_letters[first_letter].append(client)
                        else:
                            clients_by_letters[first_letter] = [client]

                context['clients_by_letters'] = clients_by_letters
            else:
                # Sort the clients based on their closest visit dates
                sentinel_datetime = datetime(9999, 12, 31, tzinfo=timezone.utc)
                sorted_clients = sorted(
                    clients_to_display,
                    key=lambda client: closest_visit_dict.get(client.id, sentinel_datetime)
                )

                context['object_list'] = sorted_clients

            context['ordering'] = ordering

        else:
            ordering = self.request.GET.get('ordering', 'closest_visit')  # Get the ordering parameter from the request
            if ordering == 'name':
                object_list = self.model.objects.order_by('name')
                clients_by_letters = {}
                for client in object_list:
                    first_letter = client.name[0].upper()
                    if first_letter.isalpha():
                        if first_letter in clients_by_letters:
                            clients_by_letters[first_letter].append(client)
                        else:
                            clients_by_letters[first_letter] = [client]

                context['clients_by_letters'] = clients_by_letters
            else:
                # Sort the clients based on their closest visit dates
                sentinel_datetime = datetime(9999, 12, 31, tzinfo=timezone.utc)
                sorted_clients = sorted(
                    all_clients,
                    key=lambda client: closest_visit_dict.get(client.id, sentinel_datetime)
                )

                context['object_list'] = sorted_clients

            context['ordering'] = ordering

        return context


class ClientVisitsEditView(RedirectPermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Client
    template_name = 'clients_data/client_visits_edit.html'

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Client.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Client.objects.all())
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        formset = VisitFormSet(**self.get_form_kwargs(), instance=self.object)
        formset.queryset = formset.queryset.exclude(completed=True)
        return formset

    def form_valid(self, form):
        formset = form

        if formset.is_valid():
            withdraw = 0
            for visit_form in formset:
                if visit_form.cleaned_data.get('completed', True):
                    visit_price = visit_form.cleaned_data.get('visit_price', 0)
                    withdraw += visit_price
            self.object.deposit -= withdraw
            self.object.save()

        else:
            context = self.get_context_data()
            context['form_errors'] = form.errors
            return context

        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('single_client', kwargs={'pk': self.object.pk, 'name': self.object.name})


class ClientPaymentsEditView(CreateView):
    model = Payment
    template_name = 'clients_data/client_payments_edit.html'
    form_class = PaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        name = self.kwargs.get('name')
        client_name = get_object_or_404(Client, pk=pk, name=name).name
        context['client_name'] = client_name
        return context

    def form_valid(self, form):
        pk = self.kwargs.get('pk')
        client = get_object_or_404(Client, pk=pk)
        form.instance.client = client

        pay_amount = form.cleaned_data.get('pay_amount')
        client.balance += pay_amount
        client.deposit += pay_amount
        client.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('single_client', kwargs={'pk': self.kwargs['pk'], 'name': self.kwargs['name']})


class SingleClientUpdateView(RedirectPermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name_suffix = "_update_form"

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')


class SingleClientDeleteView(RedirectPermissionRequiredMixin, DeleteView):
    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    model = Client
    context_object_name = 'client'
    success_url = reverse_lazy('clients_list')

    def form_valid(self, form):
        return super(SingleClientDeleteView, self).form_valid(form)


class TimetableView(RedirectPermissionRequiredMixin, TemplateView):
    template_name = 'clients_data/schedule_table.html'

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get today's date and calculate the next 9 dates
        today = datetime.today().date()
        dates = [today + timedelta(days=i) for i in range(10)]

        # Define the time range
        start_time = datetime.strptime("10:00", "%H:%M").time()
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
    template_name = 'clients_data/completed_visits.html'
    context_object_name = 'completed_visits'

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    def get_queryset(self):
        completed_visits = self.model.objects.filter(completed=True)

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
            completed_visits = self.model.objects.filter(completed=True).filter(
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
            context['ordering'] = ordering
        else:
            completed_visits = self.model.objects.filter(completed=True)
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
            context['ordering'] = ordering

        return context


class ActualVisitsListView(RedirectPermissionRequiredMixin, ListView):
    model = Visit
    template_name = 'clients_data/actual_visits.html'
    context_object_name = 'actual_visits'

    permission_required = ('clients_data.view_client',
                           'clients_data.add_client',
                           'clients_data.change_client',
                           'clients_data.delete_client')

    def get_queryset(self):
        queryset = super().get_queryset()
        actual_visits = self.model.objects.filter(completed=False)

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
        search_query = self.request.GET.get('search')  # Get the search query parameter from the request
        current_date = datetime.today().date()
        context['current_date'] = current_date

        # Filter by search query if it exists
        if search_query:
            actual_visits = self.model.objects.filter(completed=False).filter(
                Q(client__name__icontains=search_query) |
                Q(massage_type__icontains=search_query) |
                Q(visit_date__icontains=search_query) |
                Q(client__age__icontains=search_query) |
                Q(visit_time__icontains=search_query) |
                Q(visit_price__icontains=search_query)
            ).distinct()

            # Sort search by ordering
            if ordering == 'visit_date':
                actual_visits = actual_visits.order_by('visit_date')

                # Add months name in ordering
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

                # Add letters in ordering
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
            context['ordering'] = ordering

        # Sort by ordering if not search query
        else:
            actual_visits = self.model.objects.filter(completed=False)
            if ordering == 'visit_date':
                actual_visits = actual_visits.order_by('visit_date')

                # Add months name in ordering
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

                # Add letters in ordering
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
            context['ordering'] = ordering

        return context


class BalanceView(TemplateView):
    template_name = 'clients_data/balance.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['client_names'] = Client.objects.values_list('name', flat=True)

        # Get client url if exists
        client_url = self.kwargs.get('client_url')

        # Get both selections
        period_selection = self.request.GET.get('period_selection')
        client_selection = self.request.GET.get('client_selection')

        # Initialize the queryset with all payments
        queryset = Payment.objects.all()

        # Filter by period if it's selected
        if period_selection:
            if int(period_selection) < 2000:
                delta = int(period_selection)
                start_date = date.today() - timedelta(days=delta * 30)
                end_date = date.today()
            else:
                start_date = datetime(int(period_selection), 1, 1)
                end_date = datetime(int(period_selection), 12, 31)

            # Filter based on the payment date
            queryset = queryset.filter(
                Q(payment_date__gte=start_date) &
                Q(payment_date__lte=end_date)
            )

        # Filter by client if it's selected
        if client_selection and client_selection != 'all_clients':
            queryset = queryset.filter(client__name=client_selection)

        # Filter by client if we came from client's detail page
        if client_url:
            start_date = date.today() - timedelta(days=3 * 30)  # To display only last 3 months payments
            end_date = date.today()
            queryset = queryset.filter(
                Q(client__name=client_url) &
                Q(payment_date__gte=start_date) &
                Q(payment_date__lte=end_date)
            )

        context['payments'] = queryset
        context['selected_period'] = period_selection
        context['selected_client'] = client_selection
        context['client_url'] = client_url

        # Calculate balance
        total_balance = 0
        for payment in queryset:
            total_balance += payment.pay_amount

        context['total_balance'] = total_balance

        return context


# Charts views


@staff_member_required
def get_filter_options(request):
    # Get distinct year
    grouped_payments = Payment.objects.annotate(year=ExtractYear("payment_date")).values("year").order_by("-year") \
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
    payments = Payment.objects.all()

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

    payments = payments.filter(payment_date__range=[start_date, end_date])

    if client_name:
        payments = payments.filter(client__name=client_name)

    grouped_payments = payments.annotate(price=F("pay_amount")).annotate(month=ExtractMonth("payment_date")) \
        .values("month").annotate(average=Sum("pay_amount")).values("month", "average").order_by("month")

    payments_dict = service_data.get_year_dict()

    for group in grouped_payments:
        payments_dict[service_data.months_list[group["month"] - 1]] = round(group["average"], 2)

    # Calculate total_sum
    total_sum = payments.aggregate(total_sum=Sum("pay_amount"))["total_sum"] or 0

    return JsonResponse({
        "title": f"Payments in {period}",
        "data": {
            "labels": list(payments_dict.keys()),
            "datasets": [{
                "label": "Сумма (сом)",
                "backgroundColor": "#13C5DD",
                "borderColor": "#13C5DD",
                "data": list(payments_dict.values()),
            }]
        },
        "total_sum": total_sum,
    })


@staff_member_required
def statistics_view(request, client_name=None, period=None):
    return render(request, 'clients_data/balance_chart.html', {})
