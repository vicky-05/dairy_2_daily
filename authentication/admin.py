from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import *
from import_export.admin import ExportMixin
from import_export import resources
from .models import CustomUser 

class UserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'subscription')
        export_order = ('id', 'username', 'email', 'subscription')

class Contact(resources.ModelResource):
    class Meta:
        model = ContactMessage
        fields = ('id', 'name', 'email', 'message', 'created_at')
        export_order = ('id', 'name', 'email', 'message', 'created_at')


admin.site.unregister(CustomUser)
@admin.register(CustomUser)
class UserAdmin(ExportMixin,admin.ModelAdmin):
    resource_class = UserResource
    list_display = ('id',  'username','email', 'is_active','subscription')
    list_filter = ('is_active', 'subscription')

@admin.register(ContactMessage)
class ContactMessageAdmin(ExportMixin,admin.ModelAdmin):
    resource_class = Contact
    list_display = ('name', 'email', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')

admin.site.register(CardDetails)
admin.site.register(Address)
admin.site.register(PincodeArea)
admin.site.register(UserSubscription)
admin.site.register(CartItem)