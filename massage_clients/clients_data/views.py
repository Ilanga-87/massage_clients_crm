from django.http import HttpResponseRedirect
from django.views.generic import (TemplateView, ListView, CreateView, DetailView, FormView)
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.db.models import Min, F

import datetime
from datetime import datetime

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
        return VisitFormSet(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('single_client', kwargs={'pk': self.object.pk, 'name': self.object.name})







# class CreateVisitsView(CreateView):
#     model = Visit
#     form_class = VisitForm
#     template_name = "clients_data/create_visit.html"
#     success_url = '/clients-data/clients-list'
#
#     def get_success_url(self):
#         self.success_url = '/clients-data/clients-list'
#         return self.success_url
#
#     def get(self, request, *args, **kwargs):
#         current_date = datetime.now().date()
#         current_time = datetime.now().time()
#         formset = formset_factory(VisitForm, extra=0)
#         initial_data = [{'client': '1', 'visit_date': current_date, 'visit_time': current_time}]
#         formset = formset(initial=initial_data, prefix='visit')
#         visit_form = self.get_form(form_class=VisitForm)
#         return render(request, self.template_name, {'formset': formset, 'form': visit_form})
#
#     def post(self, request, *args, **kwargs):
#         visit_form = self.get_form()  # Use the get_form() method to initialize the form instance
#         formset = formset_factory(VisitForm, extra=0)(request.POST, prefix='visit')  # Provide a prefix for the formset
#
#         if visit_form.is_valid() and formset.is_valid():
#             visit_instance = visit_form.save()
#
#             for form in formset:
#                 form_instance = form.save(commit=False)
#                 form_instance.visit = visit_instance
#                 form_instance.save()
#
#             return HttpResponseRedirect(self.get_success_url())
#
#         return render(request, self.template_name, {'formset': formset, 'form': visit_form})
#
#
# class SingleClientView2(DetailView, FormMixin):
#     model = Client
#     form_class = VisitForm
#     template_name = 'clients_data/client_detail.html'
#
#     def get_success_url(self):
#         return reverse('single_client', kwargs={'pk': self.object.pk, 'name': self.object.name})
#
#     def get_context_data(self, **kwargs):
#         context = super(SingleClientView2, self).get_context_data(**kwargs)
#         context['form'] = self.get_form()
#         return context
#
#     # def get_context_data(self, **kwargs):
#     #     context = super(SingleClientView, self).get_context_data(**kwargs)
#     #     # client = self.get_object()
#     #     # visits = [
#     #     #     {'visit_date': client.visit_date, 'visit_time': client.visit_time}
#     #     # ]
#     #     # VisitFormSet = formset_factory(VisitForm, extra=1)
#     #     formset = VisitFormSet(prefix='visit-formset')
#     #     context['formset'] = formset
#     #     return context
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     # def post(self, request, *args, **kwargs):
#     #     self.object = self.get_object()
#     #     # VisitFormSet = formset_factory(VisitForm, extra=1)
#     #     formset = VisitFormSet(request.POST, prefix='visit-formset')
#     #
#     #     if formset.is_valid():
#     #         return self.form_valid(formset)
#     #     else:
#     #         return self.form_invalid(formset)
#
#     def form_valid(self, form):
#         # Here, we would record the user's interest using the message
#         # passed in form.cleaned_data['message']
#         return super(SingleClientView2, self).form_valid(form)
#
#     # def form_valid(self, formset):
#     #     client = self.get_object()
#     #     cleaned_data = formset.cleaned_data[0]
#     #     client.visit_date = cleaned_data.get('visit_date')
#     #     client.visit_time = cleaned_data.get('visit_time')
#     #     client.save()
#     #     return redirect(self.get_success_url())
#
#     # def form_invalid(self, formset):
#     #     return self.render_to_response(self.get_context_data(formset=formset))
#
#
# class SingleClientDisplay(DetailView):
#     model = Client
#
#     def get_context_data(self, **kwargs):
#         context = super(SingleClientDisplay, self).get_context_data(**kwargs)
#         context['form'] = VisitForm()
#         return context
#
#
# class CreateVisitView(CreateView, SingleObjectMixin):
#     template_name = 'clients_data/client_detail.html'
#     form_class = VisitForm
#     model = Visit
#     # success_url = reverse('single_client', kwargs={'pk': self.kwargs['pk'], 'name': self.kwargs['name']})
#
#     # def post(self, request, *args, **kwargs):
#     #     print("One")
#     #     # if not request.user.is_authenticated:
#     #     #     return HttpResponseForbidden()
#     #     # self.object = self.get_object()
#     #     return super(CreateVisitView, self).post(request, *args, **kwargs)
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return self.render_to_response(self.get_context_data(form=form))
#
#     # def get_success_url(self):
#     #     print("KWARGS: ", self.kwargs)
#     #     return reverse('single_client', kwargs={'pk': self.kwargs['pk'], 'name': self.kwargs['name']})
#
#
# class SingleClientDetailView(View):
#     def get(self, request, *args, **kwargs):
#         view = SingleClientDisplay.as_view()
#         return view(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         view = CreateVisitView.as_view()
#         return view(request, *args, **kwargs)



#
# def client_list(request):
#     clients = Client.objects.filter(is_archived=False)
#     return render(request, 'clients_data/client_list.html', {'clients': clients})
#
#
# def edit_client(request, client_id):
#     client = get_object_or_404(Client, id=client_id)
#
#     if request.method == 'POST':
#         form = ClientForm(request.POST, instance=client)
#         if form.is_valid():
#             form.save()
#             return redirect('client_list')  # Replace 'client_list' with the URL name for the client list page
#     else:
#         form = ClientForm(instance=client)
#
#     return render(request, 'clients_data/edit_client.html', {'form': form})
#
#
# """
# In this example, we have two view functions:
#
# client_list: This view fetches all the actual clients (not archived) from the database
# using the Client.objects.filter(is_archived=False) query. It then passes the clients to the template for rendering.
#
# edit_client: This view handles the editing of a specific client. It takes the client_id as a parameter
# and retrieves the corresponding client object from the database using get_object_or_404.
#
# If the request method is POST, it creates an instance of the ClientForm and
# passes the submitted data (request.POST) and the client instance (instance=client) to the form. If the form is valid, it saves the updated form data and redirects the user to the client list page (replace 'client_list' with the actual URL name for the client list page).
#
# If the request method is GET, it creates an instance of the ClientForm pre-populated
# with the client's current data (instance=client). It then passes the form to the template for rendering.
#
# You'll need to create the corresponding templates client_list.html and edit_client.html to display
# the client list and the client edit form, respectively.
#
# Make sure you have the ClientForm defined in the forms.py file, which should be located
# in the same directory as your views.
#
# With these changes, the client_list view should display a list of all actual clients,
# and the edit_client view should allow you to edit the information of a specific client.
# """
#
#
# def archived_client_list(request):
#     archived_clients = Client.objects.filter(is_archived=True)
#     return render(request, 'clients_data/archived_client_list.html', {'archived_clients': archived_clients})
#
#
# def restore_client(request, client_id):
#     client = get_object_or_404(Client, id=client_id)
#
#     if request.method == 'POST':
#         client.is_archived = False
#         client.save()
#         return redirect(
#             'archived_client_list')  # Replace 'archived_client_list' with the URL name for the archived client list page
#
#     return render(request, 'clients_data/restore_client.html', {'client': client})
#
#
# """
# In this example, we have two view functions:
#
# archived_client_list: This view fetches all the archived clients (is_archived=True) from the database
# using the Client.objects.filter(is_archived=True) query. It then passes the archived clients
# to the template for rendering.
#
# restore_client: This view handles the restoration of an archived client.
# It takes the client_id as a parameter and retrieves the corresponding client
# object from the database using get_object_or_404.
#
# If the request method is POST, it sets the is_archived field of the client to False to make it
# active again and saves the changes. Then it redirects the user to the archived client list page
# (replace 'archived_client_list' with the actual URL name for the archived client list page).
#
# If the request method is GET, it passes the client object to the template for rendering.
#
# You'll need to create the corresponding templates archived_client_list.html and restore_client.html to display
# the archived client list and the confirmation page for restoring a client, respectively.
#
# With these changes, the archived_client_list view should display a list of archived clients, and
# the restore_client view should allow you to restore a specific archived client and make them active again.
# """
#
#
# def schedule(request):
#     # Get all actual clients
#     clients = Client.objects.filter(is_archived=False).order_by('visit_days', 'visit_time')
#
#     # Prepare the schedule data
#     schedule_data = {}
#     for client in clients:
#         visit_days = client.visit_days.split(',')  # Assuming visit_days is a comma-separated string
#
#         for day in visit_days:
#             if day not in schedule_data:
#                 schedule_data[day] = []
#
#             schedule_data[day].append(client)
#
#     # Sort the schedule data by day
#     sorted_schedule_data = sorted(schedule_data.items())
#
#     return render(request, 'clients_data/schedule.html', {'schedule_data': sorted_schedule_data})
#
#
# """
# In this example, we have the schedule view that fetches all actual clients from the database and prepares
# the schedule data. It then passes the schedule data to the template for rendering.
#
# The schedule data is prepared by iterating through each client and extracting the visit days.
# We split the visit days into a list (assuming visit_days is a comma-separated string) and store the client
# in the corresponding day's entry in the schedule_data dictionary.
#
# Next, we sort the schedule_data dictionary by day using sorted() to ensure that the schedule is displayed
# in the correct order.
#
# You'll need to create the corresponding schedule.html template to display the schedule tables.
# Here's an example HTML code:
# """
#
#
# def client_list_check(request):
#     clients = Client.objects.filter(is_archived=False)
#     return render(request, 'clients_data/client_list.html', {'clients': clients})
#
#
# def archive_clients(request):
#     if request.method == 'POST':
#         client_ids = request.POST.getlist('selected_clients')
#         clients = Client.objects.filter(id__in=client_ids)
#         for client in clients:
#             client.is_archived = True
#             client.save()
#         return redirect('client_list')  # Replace 'client_list' with the URL name for the client list page
#
#     clients = Client.objects.filter(is_archived=False)
#     return render(request, 'clients_data/archive_clients.html', {'clients': clients})
#
#
# """
# In this updated example, we have two view functions:
#
# client_list: This view retrieves all the actual clients (not archived) from the database
# using the Client.objects.filter(is_archived=False) query.
# It then passes the clients to the template for rendering.
#
# archive_clients: This view handles the archiving of multiple clients.
#
# If the request method is POST, it retrieves the list of selected client IDs
# from the submitted form data (request.POST.getlist('selected_clients')). It then retrieves
# the corresponding client objects from the database and updates their is_archived field to True.
# Finally, it saves the changes and redirects the user back to the client list page
# (replace 'client_list' with the actual URL name for the client list page).
#
# If the request method is GET, it retrieves all the actual clients (not archived)
# from the database and passes them to the template for rendering.
#
# Now, let's update the HTML template to include the checkbox column and the "Archive" button:
# """
#
#
# class ClientHTMxTableView2(SingleTableMixin, FilterView):
#     model = Client
#     table_class = ClientHTMxTable
#     queryset = Client.objects.all()
#     filterset_class = ClientFilter
#     paginate_by = 15
#
#     def get_template_names(self):
#         if self.request.htmx:
#             template_name = "clients_data/client_table_partial.html"
#         else:
#             template_name = "clients_data/client_table_htmx.html"
#
#         return template_name
#
#
# class ClientHTMxTableView(SingleTableView):
#     model = Client
#     # queryset = Client.objects.all()
#     table_class = ClientHTMxTable
#     filterset_class = ClientFilter
#
#     # paginate_by = 15
#     # template_name = "clients_data/client_table_htmx.html"
#
#     def get_template_names(self):
#         if self.request.htmx:
#             template_name = "clients_data/client_table_partial.html"
#         else:
#             template_name = "clients_data/client_table_htmx.html"
#
#         return template_name
