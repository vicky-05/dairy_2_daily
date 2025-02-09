from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import *
from orders.models import Order
from django.http import JsonResponse
import json
from .forms import ProfileUpdateForm
from django.contrib import messages

User = get_user_model()  # Fetches the custom user model


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        security_question = request.POST.get('security_question')
        security_answer = request.POST.get('security_answer')

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

        if not security_question or not security_answer:
            messages.error(request, "Please select and answer a security question!")
            return redirect('register')

        # Save user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Save security question
        SecurityQuestion.objects.create(user=user, question=security_question, answer=security_answer.lower())

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

def forgot_password(request):
    return render(request, 'user/forgot_password.html')

def check_username(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        
        try:
            user = User.objects.get(username=username)
            question = SecurityQuestion.objects.get(user=user).question
            return JsonResponse({'success': True, 'question': question})
        except (User.DoesNotExist, SecurityQuestion.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Username not found!'})



def validate_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        answer = data.get('answer')

        try:
            user = User.objects.get(username=username)
            security = SecurityQuestion.objects.get(user=user)

            if security.answer.lower() == answer.lower():
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Incorrect answer!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Something went wrong! Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method!'})


def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        new_password = data.get('new_password')

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found!'})
        
@login_required
def profile_settings(request):
    user = request.user
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile_settings")  # Refresh the page after saving
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, "user/profile_settings.html", {"form": form})

@login_required
def dashboard(request):
    user = request.user


    # Fetch the latest subscription details for the logged-in user
    subscription = UserSubscription.objects.filter(user=user).first()

    # Fetch the areas assigned to the user via addresses
    assigned_areas = Address.objects.filter(user=user).values_list('pincode_area__area', flat=True)

    # Define the delivery sequence
    delivery_steps = ["Farm", "Peraiyur", "Tallakulam", "Goripalayam", "K.Pudur", "Othakadai"]

    # Get the user's assigned area and determine the required steps
    required_steps = []
    for step in delivery_steps:
        required_steps.append(step)
        if step in assigned_areas:
            break  # Include all steps up to and including the user's area

    context = {
        'user': user,
        'subscription': subscription,
        'required_steps': required_steps,  # Pass only the required steps
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
                # Retrieve the order associated with the authenticated user
                order = get_object_or_404(Order, id=order_id, user=request.user)

                # Check if the order is already canceled
                if order.status == 'Canceled':
                    return JsonResponse({"success": False, "message": "Order is already canceled."})

                # Update the order status to canceled
                order.status = 'Canceled'
                order.save()

                # Add the order amount back to the user's balance
                user = request.user  # Get the logged-in user
                user.balance = Decimal(user.balance) + Decimal(order.amount)  # Convert to Decimal before addition
                user.save()

                return JsonResponse({
                    "success": True,
                    "message": "Order canceled successfully.",
                    "new_balance": float(user.balance) 
                })

            except Order.DoesNotExist:
                return JsonResponse({"success": False, "message": "Order not found."})
        return JsonResponse({"success": False, "message": "User not authenticated."})
    return JsonResponse({"success": False, "message": "Invalid request method."})


def subscription_track(request):
    user = request.user
     # Fetch the latest subscription details for the logged-in user
    subscription = UserSubscription.objects.filter(user=user).first()

    # Fetch the areas assigned to the user via addresses
    assigned_areas = Address.objects.filter(user=user).values_list('pincode_area__area', flat=True)

    # Define the delivery sequence
    delivery_steps = ["Farm", "Peraiyur", "Tallakulam", "Goripalayam", "K.Pudur", "Othakadai"]

    # Get the user's assigned area and determine the required steps
    required_steps = []
    for step in delivery_steps:
        required_steps.append(step)
        if step in assigned_areas:
            break  # Include all steps up to and including the user's area

    context = {
        'user': user,
        'subscription': subscription,
        'assigned_areas': assigned_areas,
        'required_steps': required_steps,
        'delivery_steps': delivery_steps

    }
    return render(request, 'user/subscription_track.html', context)
