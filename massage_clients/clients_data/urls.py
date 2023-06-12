from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateClientView.as_view(), name='client_form'),  # URL for the first page with the form to fill
    # path('add-visit/', views.CreateVisitsView.as_view(), name='visits_form'),
    path('clients-list/', views.AllClientsView.as_view(), name='clients_list'),  # URL for the second page with the actual clients list
    path('clients/<int:pk>/<str:name>/', views.SingleClientDisplayView.as_view(), name='single_client'),
    path('clients/<int:pk>/<str:name>/visits/edit', views.ClientVisitsEditView.as_view(), name='client_visits_edit'),
    # path('clients-table/', views.ClientHTMxTableView.as_view(), name='client_table'),
    # path('archived-clients/', views.archived_client_list, name='archived_client_list'),  # URL for the third page with the archived clients list
    # path('schedule/', views.schedule, name='schedule'),  # URL for the fourth page with the schedule
    # path('archive-clients/', views.archive_clients, name='archive_clients'),  # URL for archiving multiple clients
    # path('restore-client/<int:client_id>/', views.restore_client, name='restore_client'),  # URL for restoring an archived client
]
