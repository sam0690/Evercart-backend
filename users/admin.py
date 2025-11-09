from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AdminProfile

User = get_user_model()

class AdminProfileInline(admin.StackedInline):
	model = AdminProfile
	can_delete = True
	extra = 0
	fields = ("display_name", "role_title", "phone", "avatar", "notes", "created_at", "updated_at")
	readonly_fields = ("created_at", "updated_at")

@admin.register(User)
class UserAdmin(BaseUserAdmin):
	list_display = ("id", "username", "email", "is_customer", "is_admin", "is_staff", "is_superuser")
	search_fields = ("username", "email")
	list_filter = ("is_customer", "is_admin", "is_staff", "is_superuser")
	fieldsets = (
		(None, {"fields": ("username", "password")} ),
		("Personal info", {"fields": ("first_name", "last_name", "email")} ),
		("Permissions", {"fields": ("is_active", "is_customer", "is_staff", "is_superuser", "is_admin", "groups", "user_permissions")} ),
		("Important dates", {"fields": ("last_login", "date_joined")} ),
	)
	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("username", "email", "password1", "password2", "is_customer", "is_staff", "is_superuser", "is_admin"),
		}),
	)
	inlines = [AdminProfileInline]

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "role_title", "display_name", "created_at")
	search_fields = ("user__username", "user__email", "role_title", "display_name")
	autocomplete_fields = ["user"]
