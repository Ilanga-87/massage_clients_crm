from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateClientView.as_view(), name='client_form'),  # URL for the first page with the form to fill
    path('clients-list/', views.AllClientsView.as_view(), name='clients_list'),  # URL for the second page with the actual clients list
    path('clients/<int:pk>/<str:name>/', views.SingleClientDisplayView.as_view(), name='single_client'),
    path('clients/<int:pk>/<str:name>/visits/edit', views.ClientVisitsEditView.as_view(), name='client_visits_edit'),
    path('clients/<int:pk>/<str:name>/client/edit', views.SingleClientUpdateView.as_view(), name='client_update'),
    # path('schedule/', views.schedule, name='schedule'),  # URL for the fourth page with the schedule
]
