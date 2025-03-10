from .models import SubscriptionPlan

def subscription_plans(request):
    return {'subscription_plans': SubscriptionPlan.objects.all()}