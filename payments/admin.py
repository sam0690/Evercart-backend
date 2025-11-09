from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "method", "amount", "status", "created_at")
    list_filter = ("method", "status", "created_at")
    search_fields = ("user__username", "order__id", "ref_id")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "order")
