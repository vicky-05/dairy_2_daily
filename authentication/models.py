from django.db import models
from django.contrib.auth.models import AbstractUser
from subscriptions.models import SubscriptionPlan  # Import your SubscriptionPlan model
from cryptography.fernet import Fernet
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from products.models import Product
from decimal import Decimal

class CustomUser(AbstractUser):
    subscription = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="users",
        help_text="The subscription plan associated with the user"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pics/",  # Saves files in 'media/profile_pics/'
        null=True, 
        blank=True, 
        default="profile_pics/default_profile.png",  # Default image
        help_text="User profile picture"
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.username

class SecurityQuestion(models.Model):
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def check_answer(self, given_answer):
        return self.answer.lower() == given_answer.lower()

    def __str__(self):
        return f"{self.user.username}'s Security Question"


    

class PincodeArea(models.Model):
    pincode = models.CharField(max_length=6)
    area = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.pincode} - {self.area}"

    class Meta:
        verbose_name = "Pincode-Area"
        verbose_name_plural = "Pincode-Areas"


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pincode_area = models.ForeignKey(PincodeArea, on_delete=models.CASCADE)
    address = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'pincode_area', 'address'], 
                name='unique_user_address'
            )
        ]

    def save(self, *args, **kwargs):
        # Check if an identical address already exists for the user
        existing_address = Address.objects.filter(
            user=self.user, 
            pincode_area=self.pincode_area, 
            address=self.address
        ).first()
        
        if existing_address:
            # Return the existing address instead of creating a new one
            self.id = existing_address.id
        else:
            # Save the new address if it doesn't exist
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address}, {self.pincode_area.area}, {self.pincode_area.pincode}"

fernet = Fernet(settings.ENCRYPTION_KEY)
# Utility to get Fernet instance
def get_fernet():
    return Fernet(settings.ENCRYPTION_KEY)

class CardDetails(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    card_number_encrypted = models.BinaryField(default=b'')  # Encrypted card number
    expiry_date = models.CharField(max_length=7)  # Format: YYYY/MM
    cvv_encrypted = models.BinaryField(default=b'')  # Encrypted CVV

    def save(self, *args, **kwargs):
        fernet = get_fernet()
        # Encrypt sensitive data
        if hasattr(self, 'raw_card_number'):  # Use raw_card_number only if it exists
            self.card_number_encrypted = fernet.encrypt(self.raw_card_number.encode())
        if hasattr(self, 'raw_cvv'):  # Use raw_cvv only if it exists
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
        return f"Card ending in {self.card_number[-4:]}"  # Mask all but last 4 digits

class UserSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user who subscribed
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)  # The plan subscribed to
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Subscription fee
    start_date = models.DateTimeField(auto_now_add=True)  # Start date of the subscription
    end_date = models.DateTimeField(null=True, blank=True)  # Optional end date for the subscription
    is_active = models.BooleanField(default=True)  # Indicates if the subscription is currently active

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
# Signal to update the CustomUser subscription field when a UserSubscription is deleted
@receiver(post_delete, sender=UserSubscription)
def update_user_subscription(sender, instance, **kwargs):
    user = instance.user
    if user.subscription == instance.plan:
        user.subscription = None  # Reset the subscription field
        user.save()

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.discounted_price * self.quantity
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name