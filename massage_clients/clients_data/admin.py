from django.contrib import admin

# Register your models here.
from .models import Client, Visit, Payment


class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number"]
    empty_value_display = "-empty-"


admin.site.register(Client, ClientAdmin)


class VisitAdmin(admin.ModelAdmin):
    list_display = ["client", "visit_date", "visit_time"]


admin.site.register(Visit, VisitAdmin)


class PaymentsAdmin(admin.ModelAdmin):
    list_display = ["client", "payment_date", "pay_amount"]


admin.site.register(Payment, PaymentsAdmin)
