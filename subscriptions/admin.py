from django.contrib import *
from django.contrib import admin
from .models import SubscriptionFeedback

# Register your models here.
from .models import SubscriptionPlan

admin.site.register(SubscriptionPlan)

@admin.register(SubscriptionFeedback)
class SubscriptionFeedbackAdmin(admin.ModelAdmin):
    list_display = ("user_name", "plan", "created_at")
    search_fields = ("user_name", "plan__name")
    list_filter = ("plan", "created_at")