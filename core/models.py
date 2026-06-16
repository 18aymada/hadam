from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# ======================
# PRODUCT MODEL
# ======================
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # File user downloads after payment
    file = models.FileField(upload_to="products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ======================
# PURCHASE MODEL (PRODUCTION SAFE)
# ======================
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Stripe webhook tracking (important for payment verification)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ======================
    # ACCESS CONTROL (72 HOURS)
    # ======================
    def is_active(self):
        return timezone.now() < self.created_at + timedelta(hours=72)

    def time_left_hours(self):
        remaining = (self.created_at + timedelta(hours=72)) - timezone.now()
        return max(0, int(remaining.total_seconds() // 3600))

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"