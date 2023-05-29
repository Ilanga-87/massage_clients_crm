import django_tables2 as tables
from .models import Client


class ClientHTMxTable(tables.Table):
    class Meta:
        model = Client
        template_name = "tables/bootstrap_htmx.html"
