from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
from authentication.models import CustomUser

# Model for storing order details
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipping', 'Shipping'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the default custom user model
        on_delete=models.CASCADE,
        related_name="orders"
    )
    product_name = models.CharField(max_length=255)
    product_slug = models.SlugField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    class Meta:
        ordering = ['-created_at']  # Orders are sorted by newest first
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.id} - {self.product_name} ({self.user.username})"

# Model for storing shipping details
class ShippingDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping_details")
    pincode = models.CharField(max_length=10)
    area = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"

# Model for storing payment details
# Utility to get Fernet instance
def get_fernet():
    return Fernet(settings.ENCRYPTION_KEY)

class PaymentDetails(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment_details')
    card_number_encrypted = models.BinaryField(default=b'')  # Encrypted card number
    expiry_date = models.CharField(max_length=7)  # Format: YYYY/MM
    cvv_encrypted = models.BinaryField(default=b'')  # Encrypted CVV

    # Non-persistent fields for raw card data
    raw_card_number = None
    raw_cvv = None

    def save(self, *args, **kwargs):
        fernet = get_fernet()
        # Encrypt sensitive data
        if self.raw_card_number:  # Use raw_card_number if provided
            self.card_number_encrypted = fernet.encrypt(self.raw_card_number.encode())
        if self.raw_cvv:  # Use raw_cvv if provided
            self.cvv_encrypted = fernet.encrypt(self.raw_cvv.encode())
        super().save(*args, **kwargs)

    @property
    def card_number(self):
        fernet = get_fernet()
        try:
            return fernet.decrypt(self.card_number_encrypted).decode()
        except Exception:
            return "Invalid Data"

    @property
    def cvv(self):
        fernet = get_fernet()
        try:
            return fernet.decrypt(self.cvv_encrypted).decode()
        except Exception:
            return "Invalid Data"

    def __str__(self):
        # Mask all but last 4 digits
        return f"Card ending in {self.card_number[-4:]}" if self.card_number else "Invalid Card Data"
