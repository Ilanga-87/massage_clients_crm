from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.CreateClientView.as_view(), name='client_form'),
    path('clients-list/', views.AllClientsView.as_view(), name='clients_list'),
    path('clients/<int:pk>/<str:name>/', views.SingleClientDisplayView.as_view(), name='single_client'),
    path('clients/<int:pk>/<str:name>/visits/edit/', views.ClientVisitsEditView.as_view(), name='client_visits_edit'),
    path('clients/<int:pk>/<str:name>/payment/edit/', views.ClientPaymentsEditView.as_view(),
         name='client_payment_edit'),
    path('clients/<int:pk>/<str:name>/completed-visits/', views.SingleClientCompletedVisits.as_view(),
         name='client_completed_visits'),
    path('clients/<int:pk>/<str:name>/client/edit/', views.SingleClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/<str:name>/client/delete/', views.SingleClientDeleteView.as_view(), name='client_delete'),
    path('schedule/', views.TimetableView.as_view(), name='schedule'),
    path('completed-visits/', views.CompletedVisitsListView.as_view(), name='completed_visits'),
    path('actual-visits/', views.ActualVisitsListView.as_view(), name='actual_visits'),
    path('balance/options/', views.get_filter_options, name='balance_options'),
    path('balance/data/<int:period>/', views.get_balance_chart, name='balance_data'),
    path('balance/chart/<str:client_name>', views.statistics_view, name='balance_chart_client'),
    path('balance/chart/', views.statistics_view, name='balance_chart'),
    re_path(r'^balance/data/last_3_months/$', views.get_balance_chart, {'period': 'last_3_months'}, name='last_3_months'),
    re_path(r'^balance/data/last_6_months/$', views.get_balance_chart, {'period': 'last_6_months'}, name='last_6_months'),
    re_path(r'^balance/data/last_year/$', views.get_balance_chart, {'period': 'last_year'}, name='last_year'),

]
