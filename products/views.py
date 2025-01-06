from django.shortcuts import render
from .models import *
from subscriptions.models import SubscriptionPlan
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.http import JsonResponse
import json
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages





context={

}
# Create your views here.
def home(request):
   
    featured_product = Product.objects.filter(is_featured=True).first()  # Fetch the first featured product
    
    # If no featured product exists, show a default one
    if not featured_product:
        featured_product = Product.objects.first()

     # Check if the user has an active subscription
    user_subscription = request.user.subscription if request.user.is_authenticated else None
    context = {
        'featured_product': featured_product,
        'user_subscription': user_subscription 
    } 
    return render(request, 'products/home.html', context)

def about(request):
    return render(request, 'about/about.html')

def blog(request):
    return render(request, 'blog/blog.html')

def organic_milk(request):
    return render(request, 'blog/organic_milk.html')

def fresh_milk(request):
    return render(request, 'blog/fresh_milk.html')

def journey_milk(request):
    return render(request, 'blog/journey_milk.html')

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variant = Product.objects.filter(name__iexact=product.name)
    selected_variant = variant.first()
    benefits = product.benefits_image
    reviews = product.reviews.all().order_by("-created_at")
     # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the user has already submitted a review for this product
        user_review = Review.objects.filter(product=product, user=request.user).first()
    else:
        user_review = None  # If the user is not authenticated, no review can be found

    related_products = Product.objects.exclude(
        slug=slug  # Optionally, exclude by slug as well
    )[:4]  # Limit to 4 related products
    subscription = None

    # Check if the user is authenticated and has a subscription
    if request.user.is_authenticated and request.user.subscription:
        subscription = request.user.subscription

    # Calculate discounted price if there's a subscription
    if subscription:
        discount_percentage = Decimal(subscription.discount_on_byproducts)  # Convert discount percentage to Decimal
        discounted_price = product.price * (1 - discount_percentage / 100)
    else:
        discounted_price = product.price

    cart = request.session.get('cart', {})


    # If the user has a subscription, calculate the discounted price for related products
    if request.user.is_authenticated and hasattr(request.user, 'subscription'):
        subscription = request.user.subscription
        for related_product in related_products:

            if subscription is not None:
                discount_percentage = Decimal(subscription.discount_on_byproducts)
            else:
                discount_percentage = Decimal(0)  # Default value or handle appropriately

            related_product.discounted_price = related_product.price * (1 - discount_percentage / 100)
    else:
        for related_product in related_products:
            related_product.discounted_price = related_product.price


    
    context['variant']=variant.values('slug','unit_name','unit')
    context['product']=product
    context['discounted_price'] = discounted_price
    context['discount_percentage'] = subscription.discount_on_byproducts if subscription else 0
    context['subscription'] = subscription
    context['benefits'] = benefits
    context['reviews'] = reviews
    context['user_review'] = user_review
    context['related_products'] = related_products
    context['selected_variant'] = selected_variant
    context['cart'] = cart

    return render(request, "products/product_detail.html", context=context)

def submit_review(request, slug):
    if request.method == 'POST':
            product = get_object_or_404(Product, slug=slug)

            # Retrieve and validate the rating
            rating = request.POST.get('reviewRating')
            

            feedback = request.POST.get('reviewText', '').strip()

            # Save the review
            review = Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                feedback=feedback,
            )

            return redirect('product_detail', slug=product.slug)



def add_to_cart(request, slug):
    # Retrieve the product
    product = get_object_or_404(Product, slug=slug)

    # Calculate discounted price if the user has a subscription
    if request.user.is_authenticated and hasattr(request.user, 'subscription'):
        subscription = request.user.subscription
        discount_percentage = Decimal(subscription.discount_on_byproducts)
        discounted_price = product.price * (1 - discount_percentage / 100)
    else:
        discounted_price = product.price

    # Get the cart from the session (initialize if it doesn't exist)
    cart = request.session.get('cart', {})
    
   # Check if the product is already in the cart
    if slug in cart:
        messages.info(request, "This product is already in your cart.")
        return redirect('cart_page')
    else:
        cart[slug] = {
            'name': product.name,
            'price': float(product.price),  # Original price
            'discounted_price': float(discounted_price),  # Discounted price
            'image': product.image.url,
            'quantity': 1,
        }
    
    # Save the cart back to the session
    request.session['cart'] = cart
    
    # Display success message
    messages.success(request, f"Added {product.name} to cart successfully.")
    
    # Redirect to the cart page
    return redirect('cart_page')


def cart_page(request):
    cart = request.session.get('cart', {})

    # Calculate total price using discounted price
    total_price = sum(item['discounted_price'] * item['quantity'] for item in cart.values())
    total_quantity = sum(item['quantity'] for item in cart.values())
    delivery_fee = 20 if total_price < 500 else 0
    final_total = total_price + delivery_fee

    context = {
        'cart': cart,
        'cart_json': json.dumps(cart),  # Serialize cart to JSON
        'total_quantity': total_quantity,
        'total_price': total_price,
        'delivery_fee': delivery_fee,
        'final_total': final_total,
    }
    
    # Add slugs to the cart context if not already included
    for slug, item in cart.items():
        item['slug'] = slug
    
    return render(request, 'products/add_to_cart.html', context=context)


def remove_from_cart(request, slug):
    # Get the cart from the session
    cart = request.session.get('cart', {})
    
    # Check if the product is in the cart
    if slug in cart:
        del cart[slug]  # Remove the product from the cart
    
    # Save the updated cart back to the session
    request.session['cart'] = cart
    
    # Redirect back to the cart page
    return redirect('cart_page')