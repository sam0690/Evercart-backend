from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import AdminProfile

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "email", "is_admin", "is_staff", "is_superuser")
	search_fields = ("username", "email")
	list_filter = ("is_admin", "is_staff", "is_superuser")

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "role_title", "display_name", "created_at")
	search_fields = ("user__username", "user__email", "role_title", "display_name")
	autocomplete_fields = ["user"]
