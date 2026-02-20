from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from user.models import User, Product, Order, send_welcome_email
from django.utils.text import slugify
import json


def distributor_signup(request):
    """Distributor signup"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'distributor/signup.html')
        
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, 'Please enter a valid 10-digit Indian mobile number!')
            return render(request, 'distributor/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'distributor/signup.html')
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered!')
            return render(request, 'distributor/signup.html')
        
        # Create distributor
        user = User.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            password=password,
            user_type='distributor'
        )
        
        # Send welcome email
        send_welcome_email(user)
        
        messages.success(request, 'Distributor account created! Please login.')
        return redirect('distributor_login')
    
    return render(request, 'distributor/signup.html')


def distributor_login(request):
    """Distributor login"""
    if request.method == 'POST':
        email_or_phone = request.POST.get('email_or_phone')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(phone=email_or_phone)
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials!')
                return render(request, 'distributor/login.html')
        
        user = authenticate(request, username=user_obj.email, password=password)
        
        if user is not None and user.user_type == 'distributor':
            login(request, user)
            return redirect('distributor_dashboard')
        elif user is not None:
            messages.error(request, 'This login is for distributors only!')
        else:
            messages.error(request, 'Invalid password!')
    
    return render(request, 'distributor/login.html')


def distributor_logout(request):
    """Distributor logout"""
    logout(request)
    return redirect('distributor_login')


@login_required
def distributor_dashboard(request):
    """Distributor dashboard - view all products added by this distributor"""
    if request.user.user_type != 'distributor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    products = Product.objects.filter(distributor=request.user).order_by('-created_at')
    
    # Get order statistics
    total_orders = Order.objects.filter(
        items__product__distributor=request.user
    ).distinct().count()
    
    total_sales = 0
    for product in products:
        total_sales += product.stock  # This is simplified
    
    context = {
        'products': products,
        'total_products': products.count(),
        'total_orders': total_orders
    }
    return render(request, 'distributor/dashboard.html', context)


@login_required
def add_product(request):
    """Add new mobile product"""
    if request.user.user_type != 'distributor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    if request.method == 'POST':
        brand = request.POST.get('brand')
        model_name = request.POST.get('model_name')
        price = request.POST.get('price')
        original_price = request.POST.get('original_price')
        discount = request.POST.get('discount', 0)
        features = request.POST.get('features')
        stock = request.POST.get('stock', 0)
        
        # Specifications (JSON)
        specifications = {
            'display': request.POST.get('display'),
            'processor': request.POST.get('processor'),
            'ram': request.POST.get('ram'),
            'storage': request.POST.get('storage'),
            'battery': request.POST.get('battery'),
            'camera_rear': request.POST.get('camera_rear'),
            'camera_front': request.POST.get('camera_front'),
            'os': request.POST.get('os'),
            'network': request.POST.get('network'),
        }
        
        # Create slug
        base_slug = slugify(f"{brand}-{model_name}")
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create product
        product = Product.objects.create(
            distributor=request.user,
            brand=brand,
            model_name=model_name,
            slug=slug,
            price=price,
            original_price=original_price if original_price else None,
            discount=discount if discount else 0,
            features=features,
            specifications=specifications,
            stock=stock if stock else 0,
            image1=request.FILES.get('image1'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),
            image4=request.FILES.get('image4'),
        )
        
        messages.success(request, f'Product {model_name} added successfully!')
        return redirect('distributor_dashboard')
    
    brands = Product.BRAND_CHOICES
    return render(request, 'distributor/add_product.html', {'brands': brands})


@login_required
def edit_product(request, product_id):
    """Edit existing product"""
    if request.user.user_type != 'distributor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id, distributor=request.user)
    
    if request.method == 'POST':
        product.brand = request.POST.get('brand')
        product.model_name = request.POST.get('model_name')
        product.price = request.POST.get('price')
        product.original_price = request.POST.get('original_price') or None
        product.discount = request.POST.get('discount', 0)
        product.features = request.POST.get('features')
        product.stock = request.POST.get('stock', 0)
        
        # Specifications
        product.specifications = {
            'display': request.POST.get('display'),
            'processor': request.POST.get('processor'),
            'ram': request.POST.get('ram'),
            'storage': request.POST.get('storage'),
            'battery': request.POST.get('battery'),
            'camera_rear': request.POST.get('camera_rear'),
            'camera_front': request.POST.get('camera_front'),
            'os': request.POST.get('os'),
            'network': request.POST.get('network'),
        }
        
        # Update images if provided
        if request.FILES.get('image1'):
            product.image1 = request.FILES.get('image1')
        if request.FILES.get('image2'):
            product.image2 = request.FILES.get('image2')
        if request.FILES.get('image3'):
            product.image3 = request.FILES.get('image3')
        if request.FILES.get('image4'):
            product.image4 = request.FILES.get('image4')
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('distributor_dashboard')
    
    brands = Product.BRAND_CHOICES
    context = {
        'product': product,
        'brands': brands
    }
    return render(request, 'distributor/edit_product.html', context)


@login_required
def delete_product(request, product_id):
    """Delete product"""
    if request.user.user_type != 'distributor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id, distributor=request.user)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('distributor_dashboard')


@login_required
def distributor_orders(request):
    """View orders for distributor's products"""
    if request.user.user_type != 'distributor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    # Get orders containing distributor's products
    orders = Order.objects.filter(
        items__product__distributor=request.user
    ).distinct().order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'distributor/orders.html', context)


@login_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.user.user_type != 'distributor':
        messages.error(request, 'Access denied!')
        return redirect('login')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        order.status = new_status
        order.save()
        
        messages.success(request, f'Order status updated to {new_status}!')
        return redirect('distributor_orders')
    
    return redirect('distributor_orders')
