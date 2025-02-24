from .models import Product

def products(request):
    return {'products': Product.objects.filter(is_featured=True).exclude(name='Milk')}

def cart_count(request):
    cart_items_count = request.session.get("cart_items_count", 0)
    print(cart_items_count)
    return {"cart_items_count": cart_items_count}
