from django.shortcuts import render
from .models import *
from subscriptions.models import SubscriptionPlan
from authentication.models import CartItem
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
from django.http import JsonResponse
import json
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Max,Sum
from django.db.models import Q
from orders.models import Order




context={

}
# Create your views here.
def home(request):

    latest_reviews = Review.objects.filter(
        id__in=Review.objects.values('user')
        .annotate(latest_id=Max('id'))
        .values('latest_id')
    )[:10]  # Limit to 10 reviews
   
    featured_product = Product.objects.filter(is_featured=True).first()  # Fetch the first featured product
    
    # If no featured product exists, show a default one
    if not featured_product:
        featured_product = Product.objects.first()

     # Check if the user has an active subscription
    user_subscription = request.user.subscription if request.user.is_authenticated else None
    context = {
        'featured_product': featured_product,
        'user_subscription': user_subscription,
        'reviews': latest_reviews 
    } 
    return render(request, 'products/home.html', context)

def about(request):
    return render(request, 'about/about.html')

def terms_condition(request):
    return render(request, 'blog/terms_condition.html')

def privacy_policy(request):
    return render(request, 'blog/privacy_policy.html')

def help(request):
    return render(request, 'blog/help_desk.html')

def blog(request):
    return render(request, 'blog/blog.html')

def organic_milk(request):
    return render(request, 'blog/organic_milk.html')

def fresh_milk(request):
    return render(request, 'blog/fresh_milk.html')

def journey_milk(request):
    return render(request, 'blog/journey_milk.html')

def search_products(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(Q(name__istartswith=query)) if query else []
    
    product_list = [
        {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'unit':product.unit,
            'unit_name': product.unit_name,
            'image': product.image.url if product.image else '/media/products/default.jpg'
        }
        for product in products
    ]
    
    return JsonResponse({'products': product_list})

def product_collection(request):
    products = Product.objects.filter(is_featured=True)
    context = {'products': products}
    return render(request, 'products/product_collection.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variant = Product.objects.filter(name__iexact=product.name)
    selected_variant = variant.first()
    benefits = product.benefits_image
    reviews = product.reviews.all().order_by("-created_at")

    has_completed_order=False
     # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the user has already submitted a review for this product
        user_review = Review.objects.filter(product=product, user=request.user).first()
        has_completed_order = Order.objects.filter(user=request.user, product_slug=product.slug, status='Completed').exists()
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

    cart = request.session.get("cart", {})  # For guest users
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart = {item.product.slug: item.quantity for item in cart_items}



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


    
    context = {
        'variant': variant.values('slug', 'unit_name', 'unit'),
        'product': product,
        'discounted_price': discounted_price,
        'discount_percentage': subscription.discount_on_byproducts if subscription else 0,
        'subscription': subscription,
        'benefits': benefits,
        'reviews': reviews,
        'user_review': user_review,
        'related_products': related_products,
        'selected_variant': selected_variant,
        'cart': cart,
        'has_completed_order': has_completed_order,
    }

    return render(request, "products/product_detail.html", context=context)




def submit_review(request, slug):
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)

        # Ensure the user is authenticated before proceeding
        if not request.user.is_authenticated:
            messages.error(request, "You need to log in to submit a review.")
            return redirect('login')  # Redirect to login if not logged in

        # Check if the user has at least one completed order for this product
        has_completed_order = Order.objects.filter(
            user=request.user,
            product_slug=product.slug,  # Ensure Order model has product_slug field
            status='Completed'
        ).exists()

        if not has_completed_order:
            messages.error(request, "You can only review products you have purchased and completed.")
            return redirect('product_detail', slug=product.slug)

        # Retrieve and validate the rating
        rating = request.POST.get('reviewRating')
        feedback = request.POST.get('reviewText', '').strip()

        if not rating:
            messages.error(request, "Please provide a rating.")
            return redirect('product_detail', slug=product.slug)

        # Save the review
        Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            feedback=feedback,
        )

        messages.success(request, "Review submitted successfully!")
        return redirect('product_detail', slug=product.slug)

    messages.error(request, "Invalid request method.")
    return redirect('product_detail', slug=slug)


    

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    discounted_price = product.price

    if request.user.is_authenticated:
        # Check for user subscription discount on by-products
        if hasattr(request.user, 'subscription'):
            subscription = request.user.subscription
            if subscription and hasattr(subscription, 'discount_on_byproducts') and subscription.discount_on_byproducts:
                discount_percentage = Decimal(subscription.discount_on_byproducts)
                discounted_price = product.price * (1 - discount_percentage / 100)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1, 'price': product.price, 'discounted_price': discounted_price}
        )
        
        if not created:
            messages.info(request, "This product is already in your cart.")
        else:
            messages.success(request, f"Added {product.name} to cart successfully.")

        # Update session cart count
        request.session['cart_items_count'] = CartItem.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
        request.session.modified = True

    else:
        # Guest user cart (session-based)
        cart = request.session.get('cart', {})
        if slug in cart:
            messages.info(request, "This product is already in your cart.")
        else:
            cart[slug] = {
                'name': product.name,
                'price': float(product.price),
                'discounted_price': float(discounted_price),
                'image': product.image.url,
                'quantity': 1,
            }
            request.session['cart'] = cart

        # Update session cart count
        request.session['cart_items_count'] = sum(item['quantity'] for item in request.session['cart'].values())
        request.session.modified = True

        messages.success(request, f"Added {product.name} to cart successfully.")

    return redirect('cart_page')

def cart_page(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart = {
            str(item.product.slug): {
                'name': item.product.name,
                'price': float(item.price),
                'discounted_price': float(item.discounted_price),
                'image': item.product.image.url,
                'quantity': item.quantity,
            } for item in cart_items
        }
    else:
        cart = request.session.get('cart', {})

    total_price = sum(item['discounted_price'] * item['quantity'] for item in cart.values())
    total_quantity = sum(item['quantity'] for item in cart.values())
    delivery_fee = 20 if total_price > 0 and total_price < 500 else 0
    final_total = total_price + delivery_fee
    product_quantities = json.dumps({item.product.slug: item.quantity for item in cart_items})

    return render(request, 'products/add_to_cart.html', {
        'cart': cart,
        'cart_json': json.dumps(cart),
        'total_quantity': total_quantity,
        'total_price': total_price,
        'delivery_fee': delivery_fee,
        'final_total': final_total,
        'product_quantities': product_quantities

    })

def update_cart_quantity(request):
    if request.method == "POST":
        data = json.loads(request.body)
        slug = data.get("slug")
        action = data.get("action")

        if request.user.is_authenticated:
            try:
                cart_item = CartItem.objects.get(user=request.user, product__slug=slug)

                if action == "increase":
                    if cart_item.quantity < 5:
                        cart_item.quantity += 1
                        cart_item.save()
                    else:
                        return JsonResponse({"error": "Maximum quantity reached!"}, status=400)

                elif action == "decrease":
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()

                # Recalculate total price and quantity
                cart_items = CartItem.objects.filter(user=request.user)
                total_price = sum(item.discounted_price * item.quantity for item in cart_items)
                total_quantity = sum(item.quantity for item in cart_items)

                # Calculate delivery fee
                delivery_fee = 20 if total_price > 0 and total_price < 500 else 0
                final_total = total_price + delivery_fee

                # Update session cart count
                request.session['cart_items_count'] = total_quantity
                request.session.modified = True

                

                return JsonResponse({
                    "quantity": cart_item.quantity if cart_item else 0,
                    "total_quantity": total_quantity,
                    "total_price": float(total_price),
                    "final_total": float(final_total),
                    "delivery_fee": float(delivery_fee),
                    "cart_items_count": total_quantity
                })

            except CartItem.DoesNotExist:
                return JsonResponse({"error": "Item not found in cart!"}, status=404)

        else:
            # Guest user cart (session-based)
            cart = request.session.get('cart', {})

            if slug in cart:
                if action == "increase":
                    if cart[slug]["quantity"] < 5:
                        cart[slug]["quantity"] += 1
                    else:
                        return JsonResponse({"error": "Maximum quantity reached!"}, status=400)

                elif action == "decrease":
                    if cart[slug]["quantity"] > 1:
                        cart[slug]["quantity"] -= 1
                    else:
                        del cart[slug]

                request.session["cart"] = cart

                # Recalculate total price and quantity
                total_price = sum(item["discounted_price"] * item["quantity"] for item in cart.values())
                total_quantity = sum(item["quantity"] for item in cart.values())

                # Calculate delivery fee
                delivery_fee = 20 if total_price > 0 and total_price < 500 else 0
                final_total = total_price + delivery_fee

                # Update session cart count
                request.session["cart_items_count"] = total_quantity
                request.session.modified = True

                return JsonResponse({
                    "quantity": cart[slug]["quantity"] if slug in cart else 0,
                    "total_quantity": total_quantity,
                    "total_price": float(total_price),
                    "final_total": float(final_total),
                    "delivery_fee": float(delivery_fee),
                    "cart_items_count": total_quantity
                })

    return JsonResponse({"error": "Invalid request"}, status=400)


def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(user=request.user, product=product).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, "Product removed from cart successfully.")

        # Update cart count
        request.session['cart_items_count'] = CartItem.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
        request.session.modified = True

    else:
        cart = request.session.get('cart', {})

        if slug in cart:
            del cart[slug]
            request.session['cart'] = cart

        # Update cart count
        request.session['cart_items_count'] = sum(item['quantity'] for item in request.session.get('cart', {}).values())
        request.session.modified = True

        messages.success(request, "Product removed from cart successfully.")

    return redirect('cart_page')


def check_product_stock(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        return JsonResponse({'available_quantity': product.quantity})  
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
