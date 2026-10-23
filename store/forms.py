from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order, Product

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone_number', 'address', 'city', 'delivery_zone']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control login-input',
                'placeholder': f'Enter {field.replace("_", " ")}'
            })

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 
            'stock', 'available', 'is_preorder', 
            'category', 'image'
        ]
