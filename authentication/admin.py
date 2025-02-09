from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(CardDetails)
admin.site.register(Address)
admin.site.register(PincodeArea)
admin.site.register(UserSubscription)