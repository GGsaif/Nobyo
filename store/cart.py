from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        # Validate stock (unless it's a preorder)
        if not product.is_preorder:
            if product.stock <= 0:
                # Out of stock - don't add
                return False
            
            if update_quantity:
                # For update, cap at available stock
                quantity = min(quantity, product.stock)
                self.cart[product_id]['quantity'] = quantity
            else:
                # For add, ensure total doesn't exceed stock
                new_quantity = self.cart[product_id]['quantity'] + quantity
                new_quantity = min(new_quantity, product.stock)
                self.cart[product_id]['quantity'] = new_quantity
        else:
            # For preorders, allow without stock limit
            if update_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity
        
        self.save()
        return True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids).count()

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_quantity(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            return 0
        return sum(self.cart[str(p.id)]['quantity'] for p in products)

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        self.session.modified = True
