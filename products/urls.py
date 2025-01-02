from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog_organic_milk/', views.organic_milk, name='organic_milk'),
    path('blog_fresh_milk/', views.fresh_milk, name='fresh_milk'),
    path('blog_journey_milk/', views.journey_milk, name='journey_milk'),
    path('product_details/<slug:slug>/', views.product_detail, name='product_detail'),
    path("submit_review/<slug:slug>/", views.submit_review, name="submit_review"),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('remove-from-cart/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    
    
]