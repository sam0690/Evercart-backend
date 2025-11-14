from django.db import models
from django.conf import settings
from orders.models import Order

User = settings.AUTH_USER_MODEL

class Payment(models.Model):
    PAYMENT_METHODS = (
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("fonepay", "Fonepay"),
        ("bank", "Bank Transfer"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    transaction_uuid = models.CharField(max_length=64, blank=True, null=True)
    product_code = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.method} - {self.status}"
