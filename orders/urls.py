from django.urls import path
from . import views
from .views import create_order


urlpatterns = [
    path('process_order/<slug:slug>/<str:price>/', views.process_order, name='process_order'),
    path('get-areas/<str:pincode>/', views.get_areas_by_pincode, name='get_areas_by_pincode'),
    path('create-order/<slug:slug>/', views.create_order, name='create_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
]