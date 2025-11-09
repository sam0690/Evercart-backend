from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    # make email unique and required
    email = models.EmailField(unique=True)
    # User type flags
    is_customer = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    # add extra fields later if needed: phone, address...
    def __str__(self):
        return self.username


class AdminProfile(models.Model):
    """
    Optional admin-only profile for custom admin dashboard metadata.
    Non-breaking: does not alter authentication or authorization flows.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile",
    )
    display_name = models.CharField(max_length=150, blank=True)
    role_title = models.CharField(max_length=100, blank=True, default="Administrator")
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"

    def __str__(self):
        return f"AdminProfile({self.user.username})"
