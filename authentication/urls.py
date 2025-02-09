from django.urls import path
from .views import register_view
from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout', views.logout_page, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('check-username/', views.check_username, name='check_username'),
    path('validate-answer/', views.validate_answer, name='validate_answer'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path("profile/settings/", views.profile_settings, name="profile_settings"),
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard page
    path('get-user-orders/', views.get_user_orders, name='get_user_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('subscription_track/', views.subscription_track, name='subscription_track'),
]