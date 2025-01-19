from django.contrib import admin
from .models import Order, ShippingDetails, PaymentDetails

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_name', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(ShippingDetails)
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'pincode', 'area', 'address')

@admin.register(PaymentDetails)
class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'masked_card_number', 'expiry_date')

    def masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}" if obj.card_number else "Invalid Card"
    masked_card_number.short_description = "Card Number"