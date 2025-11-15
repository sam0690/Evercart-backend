from django.contrib import admin
from .models import CartItem, Order, OrderItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "added_at")
    search_fields = ("user__username", "product__title")
    list_filter = ("added_at",)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "is_paid", "transaction_id", "transaction_uuid", "created_at")
    list_filter = ("status", "is_paid", "created_at")
    search_fields = ("user__username", "transaction_id")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("user", "status", "is_paid")}),
    ("Billing", {"fields": ("total", "transaction_id", "transaction_uuid")}),
    ("Shipping", {"fields": ("shipping_address", "shipping_city", "shipping_postal_code", "shipping_country", "shipping_phone")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
    inlines = [OrderItemInline]
