from django.db import models

# Create your models here.
from django.db import models

class SubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    PLAN_CHOICES = [
        ("Basic", "Basic Plan"),
        ("Standard", "Standard Plan"),
        ("Premium", "Premium Plan"),
    ]
    name = models.CharField(
        max_length=20, 
        choices=PLAN_CHOICES,
        help_text="Name of the subscription plan"
    )
    price_per_month = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Monthly cost of the subscription"
    )
    milk_quantity_per_day = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Amount of milk provided daily (in liters)"
    )
    discount_on_byproducts = models.PositiveIntegerField(
        help_text="Discount percentage on byproducts (e.g., ghee, butter)"
    )
    delivery_pause_limit = models.PositiveIntegerField(
        help_text="Maximum number of days per month delivery can be paused"
    )

    def __str__(self):
        return f"{self.get_name_display()}"

class SubscriptionFeedback(models.Model):
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.CASCADE, 
        related_name="feedbacks", 
        help_text="The subscription plan this feedback is for"
    )
    user_name = models.CharField(
        max_length=100, 
        help_text="Name of the user providing the feedback"
    )
    feedback = models.TextField(
        help_text="User's feedback about the subscription plan"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user_name} for {self.plan.name}"
