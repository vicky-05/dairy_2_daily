from django.contrib import admin
from .models import Order, ShippingDetails, PaymentDetails
from import_export.admin import ExportMixin
from django.utils.translation import gettext_lazy as _
from import_export import resources

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ('id', 'user', 'product_name', 'amount', 'status', 'created_at')
        export_order = ('id', 'user', 'product_name', 'amount', 'status', 'created_at')

@admin.register(Order)
class OrderAdmin(ExportMixin,admin.ModelAdmin):
    resource_class = OrderResource
    list_display = ('id', 'user', 'product_name', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at','product_name', 'amount')

@admin.register(ShippingDetails)
class ShippingDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'pincode', 'area', 'address')
    list_filter = ('pincode', 'area')

@admin.register(PaymentDetails)
class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'masked_card_number', 'expiry_date')

    def masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}" if obj.card_number else "Invalid Card"
    masked_card_number.short_description = "Card Number"