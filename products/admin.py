from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from authentication.models import CustomUser
from .models import (
    Product,Review
)



class UserAdmin(admin.ModelAdmin):
    list_display =  [ 'username', 'subscription' ]

admin.site.register(Product)
admin.site.register(CustomUser)
admin.site.register(User,UserAdmin)
admin.site.register(Review)