from .models import *
from django.shortcuts import render
from authentication .models import *
from django.http import JsonResponse
from products.models import Product
from django.shortcuts import render, get_object_or_404
import json
from django.views.decorators.csrf import csrf_exempt


def process_order(request, slug, price):

    # Retrieve all pincodes
    pincodes = PincodeArea.objects.values("pincode").distinct()

    product = get_object_or_404(Product, slug=slug)

    amount = float(price)
     

    context = { 
        'pincodes': pincodes,
        'product': product,
        'amount': amount

    }


    return render(request, 'order/product_order.html', context=context)

def get_areas_by_pincode(request, pincode):
    if request.method == "GET":
        areas = PincodeArea.objects.filter(pincode=pincode).values("area")
        return JsonResponse({"areas": list(areas)}, safe=False)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def create_order(request, slug):
    if request.method == 'POST':
        data = json.loads(request.body)

         # Retrieve the product using the slug
        product = get_object_or_404(Product, slug=slug)
        product_name = slug.replace('-', ' ').capitalize()


        try:
            # Create the Order
            order = Order.objects.create(
                user=request.user,
                product_name=product,  # Use the product's actual name
                product_slug=slug,
                amount=data.get("amount"),
            )

            # Save Shipping Details
            ShippingDetails.objects.create(
                order=order,
                pincode=data.get("pincode"),
                area=data.get("area"),
                address=data.get("address"),
            )

            # Save Payment Details
            payment = PaymentDetails(
                order=order,
                expiry_date=data.get("expiry_date"),
            )
            payment.raw_card_number = data.get("card_number")
            payment.raw_cvv = data.get("cvv")
            payment.save()

            return JsonResponse({"success": True, "message": "Order created successfully!", "order_id": order.id})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method."})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Ensure order belongs to the logged-in user
    context = {'order': order}
    return render(request, 'order/order_success.html',context=context)

