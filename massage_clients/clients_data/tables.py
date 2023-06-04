import django_tables2 as tables
from .models import Client


class ClientHTMxTable(tables.Table):
    class Meta:
        model = Client
        template_name = "clients_data/bootstrap_htmx.html"
        fields = ("name", "phone_number", "massage_type", "visit_days", "visit_time")
