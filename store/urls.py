from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('order-history/', views.order_history, name='order_history'),
    path('cart/drawer/', views.cart_drawer, name='cart_drawer'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Dashboard Routes
    path('admin-dashboard/', views.dashboard_index, name='dashboard_index'),
    path('admin-dashboard/products/', views.dashboard_item_list, name='dashboard_item_list'),
    path('admin-dashboard/products/add/', views.dashboard_item_add, name='dashboard_item_add'),
]
