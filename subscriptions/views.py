from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from authentication.models import *
from cryptography.fernet import Fernet
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.urls import reverse

def subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    context = {'plans': plans }
    return render(request, 'products/home.html', context)

@login_required
def subscribe_view(request, plan_id):
    # Fetch the subscription plan
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Pass the plan details to the session or directly to the next page
    request.session['selected_plan'] = {
        'name': plan.name,
        'price': float(plan.price_per_month)
    }

    # Retrieve all pincodes
    pincodes = PincodeArea.objects.values("pincode").distinct()

    context = {
        'pincodes': pincodes,
        'plan_id': plan_id,
        'selected_plan': request.session['selected_plan'], 
        'plan_name': plan.name
    }
    # Redirect to the address detail page
    return render(request, 'order/payment.html', context=context) # Replace 'address_detail' with your actual URL name

def get_areas_by_pincode(request, plan_id, pincode):
    # Fetch the subscription plan
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    if request.method == "GET":
        areas = PincodeArea.objects.filter(pincode=pincode).values("area")
        return JsonResponse({"areas": list(areas)}, safe=False)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)

# Initialize the Fernet encryption
fernet = Fernet(settings.ENCRYPTION_KEY)

@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        # Extract data from the request
        user = request.user
        plan_id = request.POST.get('plan_id')
        pincode = request.POST.get('pincode')
        area = request.POST.get('area')
        address_text = request.POST.get('address')
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Validate and fetch the subscription plan
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Save the Pincode and Area (if not already in the database)
        pincode_area, _ = PincodeArea.objects.get_or_create(
            pincode=pincode, area=area
        )

        # Save the address
        address = Address.objects.create(
            user=user,
            pincode_area=pincode_area,
            address=address_text
        )

        # Encrypt the card details
        encrypted_card_number = fernet.encrypt(card_number.encode())
        encrypted_cvv = fernet.encrypt(cvv.encode())

        # Save the card details (with encryption)
        card_details = CardDetails.objects.create(
            user=user,
            card_number_encrypted=encrypted_card_number,
            expiry_date=expiry_date,
            cvv_encrypted=encrypted_cvv
        )

         # Get current date and time (transaction date)
        transaction_date = datetime.now()

        # Calculate expiry date (28 days from the next day)
        expiry_date = transaction_date + timedelta(days=28)
        expiry_date = expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Create the user subscription
        UserSubscription.objects.create(
            user=user,
            plan=plan,
            amount=plan.price_per_month,
            start_date=transaction_date,
            end_date=expiry_date
        )

        # Update the user's subscription
        user.subscription = plan
        user.save()

         # Return JSON response with redirect URL
        return JsonResponse({'status': 'success', 'redirect_url': reverse('payment-success')})


    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def payment_success(request):
    selected_plan = request.session.get('selected_plan', None)

    if not selected_plan:
        return redirect('/')  # Redirect if no plan was selected

    context = {
        'amount_paid': f"₹ {selected_plan['price']:.2f}",
        'transcation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'plan_name': selected_plan['name'],
    }

    return render(request, 'order/payment_success.html', context)
