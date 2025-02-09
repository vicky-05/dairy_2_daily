from .models import Product

def products(request):
    return {'products': Product.objects.filter(is_featured=True).exclude(name='Milk')}

