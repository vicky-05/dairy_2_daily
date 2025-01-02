from django.urls import path
from django.conf.urls import include
from . import views


urlpatterns = [
    path('subscription_plans/', views.subscription_plans, name='subscription_plans'),
    path('subscribe/<int:plan_id>/', views.subscribe_view, name='subscribe'),
    path('subscribe/<int:plan_id>/get-areas/<str:pincode>/', views.get_areas_by_pincode, name='get_areas_by_pincode'),
     path('process-payment/', views.process_payment, name='process_payment'),
     path('payment-success/', views.payment_success, name='payment-success'),
]