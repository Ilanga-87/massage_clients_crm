from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateClientView.as_view(), name='client_form_pv'),
    path('clients-list/', views.AllClientsView.as_view(), name='clients_list_pv'),
    path('clients/<int:pk>/<str:name>/', views.SingleClientDisplayView.as_view(), name='single_client_pv'),
    path('clients/<int:pk>/<str:name>/visits/edit', views.ClientVisitsEditView.as_view(), name='client_visits_edit_pv'),
    path('clients/<int:pk>/<str:name>/client/edit', views.SingleClientUpdateView.as_view(), name='client_update_pv'),
    path('clients/<int:pk>/<str:name>/client/delete/', views.SingleClientDeleteView.as_view(), name='client_delete_pv'),
    path('schedule/', views.TimetableView.as_view(), name='schedule_pv'),
    path('completed-visits/', views.CompletedVisitsListView.as_view(), name='completed_visits_pv'),
    path('clients/<int:pk>/<str:name>/completed-visits/', views.SingleClientCompletedVisits.as_view(),
         name='client_completed_visits_pv'),
    path('actual-visits/', views.ActualVisitsListView.as_view(), name='actual_visits_pv'),
    # balance part
    path('balance/options/', views.get_filter_options, name='balance_options_pv'),
    path('balance/data/<int:period>/', views.get_balance_chart, name='balance_data_pv'),
    path('balance/chart/<str:client_name>', views.statistics_view, name='balance_chart_client_pv'),
    path('balance/chart/', views.statistics_view, name='balance_chart_pv'),
]
