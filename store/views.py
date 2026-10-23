from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.db import transaction
import logging

from django.contrib.admin.views.decorators import staff_member_required
from .models import Category, Product, Order, OrderItem
from .forms import OrderCreateForm, UserRegisterForm, ProductForm
from .cart import Cart

logger = logging.getLogger(__name__)

def product_list(request, category_slug=None):
    try:
        category = None
        categories = Category.objects.all()
        # Optimize query with select_related
        products = Product.objects.filter(available=True).select_related('category')
        
        # Search functionality
        search_query = request.GET.get('q', '').strip()
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            logger.info(f"Search query: {search_query}, Results: {products.count()}")
        
        # Sorting logic
        sort = request.GET.get('sort', 'newest')
        if sort == 'newest':
            products = products.order_by('-created')
        elif sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
            
        # Filter logic
        is_preorder = request.GET.get('preorder') == 'true'
        is_stock_out = request.GET.get('stock_out') == 'true'
        
        if is_preorder:
            products = products.filter(is_preorder=True)
        if is_stock_out:
            products = products.filter(stock=0)

        categorized_products = []
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        else:
            # For the home page, group products by category (only if not searching)
            if not search_query:
                for cat in categories:
                    cat_products = products.filter(category=cat)[:10]
                    if cat_products.exists():
                        categorized_products.append({
                            'category': cat,
                            'products': cat_products
                        })

        # Pagination
        paginator = Paginator(products, 24)  # 24 products per page
        page = request.GET.get('page', 1)
        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)

        return render(request, 'store/product_list.html', {
            'category': category,
            'categories': categories,
            'products': products_page,
            'categorized_products': categorized_products,
            'current_sort': sort,
            'is_preorder': is_preorder,
            'is_stock_out': is_stock_out,
            'search_query': search_query
        })
    except Exception as e:
        logger.error(f"Error in product_list: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading products.")
        return render(request, 'store/product_list.html', {
            'categories': Category.objects.all(),
            'products': [],
            'categorized_products': []
        })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product has stock (unless it's a preorder)
    if not product.is_preorder and product.stock <= 0:
        messages.warning(request, f"{product.name} is out of stock.")
        return redirect('store:product_detail', id=product.id, slug=product.slug)
    
    # Check if adding one more would exceed stock
    current_quantity = cart.cart.get(str(product.id), {}).get('quantity', 0)
    if not product.is_preorder and (current_quantity + 1) > product.stock:
        messages.warning(request, f"Only {product.stock} items available. Currently have {current_quantity} in cart.")
        return redirect('store:product_detail', id=product.id, slug=product.slug)
    
    cart.add(product=product, quantity=1)
    messages.success(request, f"{product.name} added to cart.")
    return redirect('store:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('store:cart_detail')

@require_POST
def cart_update(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate stock
        if quantity > product.stock and not product.is_preorder:
            messages.warning(request, f"Only {product.stock} items available in stock.")
            quantity = product.stock
        
        if quantity > 0:
            cart.add(product=product, quantity=quantity, update_quantity=True)
            messages.success(request, "Cart updated successfully.")
        else:
            cart.remove(product)
            messages.info(request, "Item removed from cart.")
    except ValueError:
        messages.error(request, "Invalid quantity.")
        logger.error(f"Invalid quantity in cart_update: {request.POST.get('quantity')}")
    except Exception as e:
        messages.error(request, "An error occurred while updating the cart.")
        logger.error(f"Error in cart_update: {str(e)}", exc_info=True)
    
    return redirect('store:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    # Check if any items in cart are no longer available
    out_of_stock_items = []
    items_to_remove = []
    
    # Collect the items to check
    cart_items = list(cart)
    
    for item in cart_items:
        product = item['product']
        quantity = item['quantity']
        
        # Check if product is out of stock (and not a preorder)
        if not product.is_preorder and product.stock == 0:
            out_of_stock_items.append(product.name)
            items_to_remove.append(product)
        # Check if quantity exceeds available stock
        elif not product.is_preorder and quantity > product.stock:
            out_of_stock_items.append(f"{product.name} (only {product.stock} available, had {quantity})")
            cart.add(product=product, quantity=product.stock, update_quantity=True)
    
    # Remove out of stock items
    for product in items_to_remove:
        cart.remove(product)
    
    if out_of_stock_items:
        messages.warning(request, f"Some items are no longer available or have limited stock: {', '.join(out_of_stock_items)}")
    
    return render(request, 'store/cart_detail.html', {'cart': cart})

def cart_drawer(request):
    cart = Cart(request)
    return render(request, 'store/includes/cart_drawer_content.html', {'cart': cart})

@login_required(login_url='store:login')
def checkout(request):
    try:
        cart = Cart(request)
        if not cart:
            messages.info(request, "Your cart is empty.")
            return redirect('store:product_list')
            
        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.user = request.user
                
                # Map delivery zones to charges
                charges = {
                    'inside_dhaka': 80,
                    'dhaka_subcity': 120,
                    'outside_dhaka': 140
                }
                zone = form.cleaned_data['delivery_zone']
                order.delivery_charge = charges.get(zone, 80)
                
                order.save()
                
                # Use atomic transaction to ensure consistency
                with transaction.atomic():
                    for item in cart:
                        product = item['product']
                        quantity = item['quantity']
                        
                        # Create order item
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=item['price'],
                            quantity=quantity
                        )
                        
                        # Decrease product stock only for non-preorder items
                        if not product.is_preorder and product.stock > 0:
                            product.stock -= quantity
                            product.stock = max(0, product.stock)  # Ensure stock doesn't go below 0
                            product.save(update_fields=['stock'])
                            logger.info(f"Stock decreased for {product.name}: -{quantity}, New stock: {product.stock}")
                
                cart.clear()
                logger.info(f"Order {order.id} created for user {request.user.username}")
                messages.success(request, "Your order has been placed successfully!")
                return render(request, 'store/order_success.html', {'order': order})
        else:
            # Pre-fill name if user is logged in
            form = OrderCreateForm(initial={'full_name': request.user.get_full_name() or request.user.username})
        
        return render(request, 'store/checkout.html', {'cart': cart, 'form': form})
    except Exception as e:
        logger.error(f"Error in checkout: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect('store:cart_detail')

def register(request):
    if request.user.is_authenticated:
        next_url = request.POST.get('next') or request.GET.get('next') or 'store:product_list'
        return redirect(next_url)

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            next_url = request.POST.get('next') or request.GET.get('next') or 'store:product_list'
            return redirect(next_url)
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        next_url = request.POST.get('next') or request.GET.get('next') or 'store:product_list'
        return redirect(next_url)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            messages.success(request, f"Welcome back, {user.get_full_name() or username}!")
            # Redirect to next parameter or product list
            next_url = request.POST.get('next') or request.GET.get('next') or 'store:product_list'
            return redirect(next_url)
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('store:product_list')

@login_required(login_url='store:login')
def order_history(request):
    try:
        # Optimize query with prefetch_related
        orders = Order.objects.filter(user=request.user).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        ).order_by('-created')
        
        # Pagination for order history
        paginator = Paginator(orders, 10)  # 10 orders per page
        page = request.GET.get('page', 1)
        try:
            orders_page = paginator.page(page)
        except PageNotAnInteger:
            orders_page = paginator.page(1)
        except EmptyPage:
            orders_page = paginator.page(paginator.num_pages)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'store/includes/order_history_list.html', {'orders': orders_page})
        return render(request, 'store/order_history.html', {'orders': orders_page})
    except Exception as e:
        logger.error(f"Error in order_history: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading your order history.")
        return render(request, 'store/order_history.html', {'orders': []})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})

@staff_member_required
def dashboard_index(request):
    total_products = Product.objects.count()
    active_products = Product.objects.filter(available=True).count()
    total_orders = Order.objects.count()
    revenue = sum(order.get_total_cost() for order in Order.objects.all())
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'revenue': revenue,
    }
    return render(request, 'store/dashboard/index.html', context)

@staff_member_required
def dashboard_item_list(request):
    products = Product.objects.all().order_by('-created')
    context = {'products': products}
    return render(request, 'store/dashboard/item_list.html', context)

@staff_member_required
def dashboard_item_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('store:dashboard_item_list')
    else:
        form = ProductForm()
        
    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'store/dashboard/item_form.html', context)

