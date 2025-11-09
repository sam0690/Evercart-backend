from django.contrib import admin
from .models import Product, Category, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary")
    fk_name = "product"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "inventory", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "category")}),
        ("Inventory & Pricing", {"fields": ("price", "inventory")}),
        ("Details", {"fields": ("description",)}),
        ("Metadata", {"fields": ("created_at",)}),
    )
    readonly_fields = ("created_at",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
