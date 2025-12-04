from django.contrib.auth.models import AbstractUser
from django.db import models
import pyotp   # <-- YES, this stays here!

# Role options
ROLE_CHOICES = (
    ('government', 'Government'),
    ('ngo', 'NGO'),
    ('enterprise', 'Enterprise'),
    ('developer', 'Developer'),
)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Google Authenticator Secret Key
    otp_secret = models.CharField(max_length=32, default=pyotp.random_base32)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Django still needs username internally

    def __str__(self):
        return self.email

    def get_totp(self):
        return pyotp.TOTP(self.otp_secret)


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"
    
