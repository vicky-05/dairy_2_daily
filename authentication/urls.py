from django.urls import path
from .views import register_view
from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
    path('get-user-orders/', views.get_user_orders, name='get_user_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]