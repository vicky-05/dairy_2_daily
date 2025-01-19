from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import *
from products.models import Product
from orders.models import Order
from django.http import JsonResponse



User = get_user_model()  # Fetches the custom user model
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('register')

        # Save user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'user/register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  # Redirect to home page after successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')  # Redirect back to login page if authentication fails

    return render(request, 'user/login.html')

def logout_page(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user

    # Fetch the latest subscription details for the logged-in user
    subscription = UserSubscription.objects.filter(user=user).first()
    

    context = {
        'user': user,
        'subscription': subscription,
        
    }

    return render(request, 'user/dashboard.html', context)

@login_required
def get_user_orders(request):
    try:
        user_orders = Order.objects.filter(user=request.user).values(
            'id', 'product_name', 'status', 'amount'
        )
        orders = list(user_orders)  # Convert QuerySet to a list of dictionaries
        return JsonResponse({'success': True, 'orders': orders})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def cancel_order(request, order_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                # Retrieve the order
                order = Order.objects.get(id=order_id, user=request.user)

                # Check if the order is already canceled
                if order.status == 'Canceled':
                    return JsonResponse({"success": False, "message": "Order is already canceled."})

                # Update the status to canceled
                order.status = 'Canceled'
                order.save()

                return JsonResponse({"success": True, "message": "Order canceled successfully."})
            except Order.DoesNotExist:
                return JsonResponse({"success": False, "message": "Order not found."})
        return JsonResponse({"success": False, "message": "User not authenticated."})
    return JsonResponse({"success": False, "message": "Invalid request method."})