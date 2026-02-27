from .cart import Cart
from .models import Category

def cart_processor(request):
    return {
        'cart': Cart(request),
        'categories': Category.objects.all() # Make categories available globally
    }
