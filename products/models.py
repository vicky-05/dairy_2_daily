from django.db import models
from django.utils.text import slugify  # For generating slugs
from subscriptions.models import SubscriptionPlan
from django.conf import settings
from django.shortcuts import render
from decimal import Decimal
# Create your models here.
# Product Model
# Variant Model

    
class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)  # Slug field
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)  # Add this field to track stock
    image = models.ImageField(upload_to="products/images/", default="products/default.jpg")
    product_video = models.FileField(upload_to="products/videos/", blank=True, null=True)  # Allow video file upload
    unit_name = models.CharField(max_length=50, blank=True, null=True)  # E.g., "500ml", "1kg"
    unit = models.CharField(
        max_length=2,
        choices=[('ml', 'Milliliters (ml)'), ('l', 'Liters (l)'), ('mg', 'Milligrams (mg)'), ('gm', 'Grams (gm)')],
        default='ml',
    )
    display_order = models.PositiveIntegerField(default=0)
    nutrient_facts = models.JSONField(default=dict)
    benefits_image = models.JSONField(default=dict)
    is_featured = models.BooleanField(default=False)  # New field to mark featured products
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New field

    def save(self, *args, **kwargs):
        # Calculate discounted price if a subscription plan exists
        if self.subscription_plan:
            discount_percentage = Decimal(self.subscription_plan.discount_on_byproducts)
            self.discounted_price = self.price * (1 - discount_percentage / 100)
        else:
            self.discounted_price = self.price
        super().save(*args, **kwargs)  # Call the base class save method

    def __str__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        # Automatically generate a slug if it's not provided
        if not self.slug:
            base_slug = slugify(self.name)  # Create a base slug from the product name
            slug = base_slug
            counter = 1

            # Ensure the slug is unique by appending a counter or variant identifier
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super(Product, self).save(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Rating from 1 to 5
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"


