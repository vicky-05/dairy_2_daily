from django.urls import path
from . import views

urlpatterns = [
    path('employee/', views.employee_list, name='employee_list'),  # Employee list view
    path('employee/add/', views.employee_add, name='employee_add'),  # Add new employee view
    path('employee/edit/<int:pk>/', views.employee_edit, name='employee_edit'),  # Edit employee view
    path('employee/delete/<int:pk>/', views.employee_delete, name='employee_delete'),  # Delete employee view
    path('employee/login/', views.employee_login, name='employee_login'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/logout/', views.employee_logout, name='employee_logout'),
    path('manage-orders/', views.manage_orders, name='manage_product_orders'),
    path('subscription-orders/', views.subscription_orders, name='subscription_orders'),

]
