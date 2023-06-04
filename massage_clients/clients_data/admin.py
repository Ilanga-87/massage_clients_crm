from django.contrib import admin

# Register your models here.
from .models import Client, Visit


class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "massage_type"]
    empty_value_display = "-empty-"


admin.site.register(Client, ClientAdmin)


class VisitAdmin(admin.ModelAdmin):
    list_display = ["client", "visit_date", "visit_time"]


admin.site.register(Visit, VisitAdmin)
