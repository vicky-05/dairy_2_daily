from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_products, name='search_products'),
    path('about/', views.about, name='about'),
    path('terms_condition/',views.terms_condition,name='terms_condition'),
    path('privacy_policy/',views.privacy_policy,name='privacy_policy'),
    path('help/', views.help, name='help'),
    path('blog/', views.blog, name='blog'),
    path('blog_organic_milk/', views.organic_milk, name='organic_milk'),
    path('blog_fresh_milk/', views.fresh_milk, name='fresh_milk'),
    path('blog_journey_milk/', views.journey_milk, name='journey_milk'),
    path('product_collection/', views.product_collection, name='product_collection'),
    path('product_details/<slug:slug>/', views.product_detail, name='product_detail'),
    path("submit_review/<slug:slug>/", views.submit_review, name="submit_review"),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('check-stock/<slug:slug>/', views.check_product_stock, name='check_product_stock'),
    path('remove-from-cart/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    
    
]