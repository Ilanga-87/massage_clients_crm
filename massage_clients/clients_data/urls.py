from django.urls import path
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
    path('schedule/', views.TimetableView.as_view(), name='schedule'),
    path('completed-visits/', views.CompletedVisitsListView.as_view(), name='completed_visits'),
    path('actual-visits/', views.ActualVisitsListView.as_view(), name='actual_visits'),
    path('balance/<str:client_url>/', views.BalanceView.as_view(), name='balance_client'),
    path('balance/', views.BalanceView.as_view(), name='balance'),
]
