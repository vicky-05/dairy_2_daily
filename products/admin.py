from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from authentication.models import CustomUser
from import_export.admin import ExportMixin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from .models import (
    Product,Review

)

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'quantity', 'unit_name', 'unit')
        export_order = ('id', 'name', 'price', 'quantity', 'unit_name', 'unit')

class UserAdmin(admin.ModelAdmin):
    list_display =  [ 'username', 'subscription' ]

@admin.register(Product)
class ProductAdmin(ExportMixin,admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ['id','name', 'price', 'quantity','unit_name','unit']
    list_filter = ['price', 'quantity', 'unit_name']
    search_fields = ['name', 'description']
    list_per_page = 10


admin.site.register(CustomUser)
admin.site.register(User,UserAdmin)
admin.site.register(Review)