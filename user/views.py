from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import User, Product, Cart, Order, OrderItem, Review, send_welcome_email, send_order_sms
import json
from django.utils import timezone


def index(request):
    """Home page redirect to shopping"""
    return redirect('shopping')


def signup(request):
    """User signup with phone, email, password"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type', 'user')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'user/signup.html')
        
        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, 'Please enter a valid 10-digit Indian mobile number!')
            return render(request, 'user/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'user/signup.html')
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered!')
            return render(request, 'user/signup.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            password=password,
            user_type=user_type
        )
        
        # Send welcome email
        send_welcome_email(user)
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'user/signup.html')


def user_login(request):
    """Login with email or phone"""
    if request.method == 'POST':
        email_or_phone = request.POST.get('email_or_phone')
        password = request.POST.get('password')
        
        # Try to find user by email or phone
        try:
            user_obj = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(phone=email_or_phone)
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials!')
                return render(request, 'user/login.html')
        
        # Check if user is a distributor - reject if so
        if user_obj.user_type == 'distributor':
            messages.error(request, 'Distributors must login through the distributor login page!')
            return render(request, 'user/login.html')
        
        user = authenticate(request, username=user_obj.email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('shopping')
        else:
            messages.error(request, 'Invalid password!')
    
    return render(request, 'user/login.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


@login_required
def shopping(request):
    """Shopping page with all products"""
    products = Product.objects.filter(is_available=True)
    brands = Product.BRAND_CHOICES
    
    # Filter by brand
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand=brand_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(model_name__icontains=search)
    
    context = {
        'products': products,
        'brands': brands,
        'selected_brand': brand_filter,
        'search': search
    }
    return render(request, 'user/shopping.html', context)


@login_required
def product_detail(request, product_id):
    """Product detail page with specifications, features, pictures, reviews"""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    
    # Calculate average rating
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum([r.rating for r in reviews]) / reviews.count()
    
    # Check if product is in cart
    in_cart = False
    if request.user.is_authenticated:
        in_cart = Cart.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'in_cart': in_cart
    }
    return render(request, 'user/product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if product.stock < quantity:
            messages.error(request, 'Insufficient stock!')
            return redirect('product_detail', product_id=product_id)
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.brand} {product.model_name} added to cart!')
        return redirect('cart')
    
    return redirect('product_detail', product_id=product_id)


@login_required
def cart_view(request):
    """View cart"""
    cart_items = Cart.objects.filter(user=request.user)
    total = sum([item.get_total_price() for item in cart_items])
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'user/cart.html', context)


@login_required
def remove_from_cart(request, cart_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('cart')


@login_required
def update_cart(request, cart_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        return JsonResponse({'success': True})
    
    return redirect('cart')


@login_required
def checkout(request):
    """Checkout with delivery details"""
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('shopping')
    
    total = sum([item.get_total_price() for item in cart_items])
    
    if request.method == 'POST':
        # Get delivery details
        delivery_name = request.POST.get('delivery_name')
        delivery_phone = request.POST.get('delivery_phone')
        delivery_email = request.POST.get('delivery_email')
        delivery_address = request.POST.get('delivery_address')
        
        # Get live location
        delivery_location = None
        if request.POST.get('latitude') and request.POST.get('longitude'):
            delivery_location = {
                'latitude': request.POST.get('latitude'),
                'longitude': request.POST.get('longitude')
            }
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            delivery_name=delivery_name,
            delivery_phone=delivery_phone,
            delivery_email=delivery_email,
            delivery_address=delivery_address,
            delivery_location=delivery_location,
            total_amount=total
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=f"{item.product.brand} {item.product.model_name}",
                product_price=item.product.get_discounted_price(),
                quantity=item.quantity
            )
        
        # Clear cart
        cart_items.delete()
        
        # Redirect to payment options page
        return redirect('payment_options', order_id=order.order_id)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'user/checkout.html', context)


@login_required
def payment_options(request, order_id):
    """Display payment options page"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'user/payment_options.html', context)


@login_required
def process_payment(request):
    """Process payment - handles Cash on Delivery"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        payment_method = request.POST.get('payment_method')
        
        try:
            order = Order.objects.get(order_id=order_id, user=request.user)
            
            if payment_method == 'cod':
                # Cash on Delivery - confirm order
                order.payment_status = 'pending'
                order.status = 'confirmed'
                order.save()
                
                # Send order confirmation SMS
                send_order_sms(order.delivery_phone, order.order_id, 'confirmed')
                
                # Redirect to order confirmation with success message
                messages.success(request, 'Order placed successfully! You will pay when you receive your order.')
                return redirect('order_confirmation', order_id=order.order_id)
            else:
                # Other payment methods - show message
                messages.info(request, 'This feature will be updated soon. Please choose Cash on Delivery.')
                return redirect('payment_options', order_id=order_id)
                
        except Order.DoesNotExist:
            messages.error(request, 'Order not found!')
            return redirect('shopping')
    
    return redirect('shopping')


@csrf_exempt
@login_required
def payment_callback(request):
    """Payment callback - No longer used with new payment system"""
    return JsonResponse({'success': False, 'error': 'Payment callback not available. Please use Cash on Delivery.'})


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'user/order_confirmation.html', context)


@login_required
def orders(request):
    """View all orders"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/orders.html', {'orders': orders})


@login_required
def add_review(request, product_id):
    """Add review to product"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        # Check if user already reviewed
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'Review updated!')
        else:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Review added!')
        
        return redirect('product_detail', product_id=product_id)
    
    return redirect('product_detail', product_id=product_id)


@login_required
def buy_now(request, product_id):
    """Buy now - directly go to checkout with single product"""
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock < 1:
        messages.error(request, 'Product out of stock!')
        return redirect('product_detail', product_id=product_id)
    
    # Get quantity
    quantity = int(request.POST.get('quantity', 1))
    
    # Calculate total
    total = product.get_discounted_price() * quantity
    
    # Store product and quantity in session for checkout
    request.session['buy_now_product_id'] = product.id
    request.session['buy_now_quantity'] = quantity
    
    return redirect('checkout_buy_now')


@login_required
def checkout_buy_now(request):
    """Checkout for buy now"""
    product_id = request.session.get('buy_now_product_id')
    quantity = request.session.get('buy_now_quantity', 1)
    
    if not product_id:
        messages.error(request, 'No product selected!')
        return redirect('shopping')
    
    product = get_object_or_404(Product, id=product_id)
    total = product.get_discounted_price() * quantity
    
    if request.method == 'POST':
        delivery_name = request.POST.get('delivery_name')
        delivery_phone = request.POST.get('delivery_phone')
        delivery_email = request.POST.get('delivery_email')
        delivery_address = request.POST.get('delivery_address')
        
        delivery_location = None
        if request.POST.get('latitude') and request.POST.get('longitude'):
            delivery_location = {
                'latitude': request.POST.get('latitude'),
                'longitude': request.POST.get('longitude')
            }
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            delivery_name=delivery_name,
            delivery_phone=delivery_phone,
            delivery_email=delivery_email,
            delivery_address=delivery_address,
            delivery_location=delivery_location,
            total_amount=total
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=f"{product.brand} {product.model_name}",
            product_price=product.get_discounted_price(),
            quantity=quantity
        )
        
        # Clear session
        del request.session['buy_now_product_id']
        del request.session['buy_now_quantity']
        
        # Redirect to payment options page
        return redirect('payment_options', order_id=order.order_id)
    
    context = {
        'product': product,
        'quantity': quantity,
        'total': total
    }
    return render(request, 'user/checkout_buy_now.html', context)
