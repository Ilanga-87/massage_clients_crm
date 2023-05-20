from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import ClientForm
from .models import Client


def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')  # Replace 'client_list' with the URL name for the client list page
    else:
        form = ClientForm()

    return render(request, 'clients_data/client_list.html', {'form': form})


def client_list(request):
    clients = Client.objects.filter(is_archived=False)
    return render(request, 'clients_data/client_list.html', {'clients': clients})


def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')  # Replace 'client_list' with the URL name for the client list page
    else:
        form = ClientForm(instance=client)

    return render(request, 'clients_data/edit_client.html', {'form': form})


"""
In this example, we have two view functions:

client_list: This view fetches all the actual clients (not archived) from the database 
using the Client.objects.filter(is_archived=False) query. It then passes the clients to the template for rendering.

edit_client: This view handles the editing of a specific client. It takes the client_id as a parameter 
and retrieves the corresponding client object from the database using get_object_or_404.

If the request method is POST, it creates an instance of the ClientForm and 
passes the submitted data (request.POST) and the client instance (instance=client) to the form. If the form is valid, it saves the updated form data and redirects the user to the client list page (replace 'client_list' with the actual URL name for the client list page).

If the request method is GET, it creates an instance of the ClientForm pre-populated 
with the client's current data (instance=client). It then passes the form to the template for rendering.

You'll need to create the corresponding templates client_list.html and edit_client.html to display 
the client list and the client edit form, respectively.

Make sure you have the ClientForm defined in the forms.py file, which should be located 
in the same directory as your views.

With these changes, the client_list view should display a list of all actual clients, 
and the edit_client view should allow you to edit the information of a specific client.
"""


def archived_client_list(request):
    archived_clients = Client.objects.filter(is_archived=True)
    return render(request, 'clients_data/archived_client_list.html', {'archived_clients': archived_clients})


def restore_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        client.is_archived = False
        client.save()
        return redirect(
            'archived_client_list')  # Replace 'archived_client_list' with the URL name for the archived client list page

    return render(request, 'clients_data/restore_client.html', {'client': client})


"""
In this example, we have two view functions:

archived_client_list: This view fetches all the archived clients (is_archived=True) from the database 
using the Client.objects.filter(is_archived=True) query. It then passes the archived clients 
to the template for rendering.

restore_client: This view handles the restoration of an archived client. 
It takes the client_id as a parameter and retrieves the corresponding client 
object from the database using get_object_or_404.

If the request method is POST, it sets the is_archived field of the client to False to make it 
active again and saves the changes. Then it redirects the user to the archived client list page 
(replace 'archived_client_list' with the actual URL name for the archived client list page).

If the request method is GET, it passes the client object to the template for rendering.

You'll need to create the corresponding templates archived_client_list.html and restore_client.html to display 
the archived client list and the confirmation page for restoring a client, respectively.

With these changes, the archived_client_list view should display a list of archived clients, and 
the restore_client view should allow you to restore a specific archived client and make them active again.
"""


def schedule(request):
    # Get all actual clients
    clients = Client.objects.filter(is_archived=False).order_by('visit_days', 'visit_time')

    # Prepare the schedule data
    schedule_data = {}
    for client in clients:
        visit_days = client.visit_days.split(',')  # Assuming visit_days is a comma-separated string

        for day in visit_days:
            if day not in schedule_data:
                schedule_data[day] = []

            schedule_data[day].append(client)

    # Sort the schedule data by day
    sorted_schedule_data = sorted(schedule_data.items())

    return render(request, 'clients_data/schedule.html', {'schedule_data': sorted_schedule_data})


"""
In this example, we have the schedule view that fetches all actual clients from the database and prepares 
the schedule data. It then passes the schedule data to the template for rendering.

The schedule data is prepared by iterating through each client and extracting the visit days. 
We split the visit days into a list (assuming visit_days is a comma-separated string) and store the client 
in the corresponding day's entry in the schedule_data dictionary.

Next, we sort the schedule_data dictionary by day using sorted() to ensure that the schedule is displayed 
in the correct order.

You'll need to create the corresponding schedule.html template to display the schedule tables. 
Here's an example HTML code:
"""


def client_list_check(request):
    clients = Client.objects.filter(is_archived=False)
    return render(request, 'clients_data/client_list.html', {'clients': clients})


def archive_clients(request):
    if request.method == 'POST':
        client_ids = request.POST.getlist('selected_clients')
        clients = Client.objects.filter(id__in=client_ids)
        for client in clients:
            client.is_archived = True
            client.save()
        return redirect('client_list')  # Replace 'client_list' with the URL name for the client list page

    clients = Client.objects.filter(is_archived=False)
    return render(request, 'clients_data/archive_clients.html', {'clients': clients})


"""
In this updated example, we have two view functions:

client_list: This view retrieves all the actual clients (not archived) from the database 
using the Client.objects.filter(is_archived=False) query. 
It then passes the clients to the template for rendering.

archive_clients: This view handles the archiving of multiple clients.

If the request method is POST, it retrieves the list of selected client IDs 
from the submitted form data (request.POST.getlist('selected_clients')). It then retrieves 
the corresponding client objects from the database and updates their is_archived field to True. 
Finally, it saves the changes and redirects the user back to the client list page 
(replace 'client_list' with the actual URL name for the client list page).

If the request method is GET, it retrieves all the actual clients (not archived) 
from the database and passes them to the template for rendering.

Now, let's update the HTML template to include the checkbox column and the "Archive" button:
"""