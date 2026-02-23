from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone



class User(AbstractUser):
    """Custom User model with Indian phone number and user type"""
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('distributor', 'Distributor'),
    ]
    
    phone = models.CharField(max_length=10, unique=True, help_text="Indian mobile number (10 digits)")
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']
    
    def __str__(self):
        return self.email


class Distributor(User):
    """Proxy model for Distributor users - allows separate admin interface"""
    
    class Meta:
        proxy = True
        verbose_name = 'Distributor'
        verbose_name_plural = 'Distributors'


class Product(models.Model):
    """Mobile product model with brand, model, specifications, features, and price"""
    BRAND_CHOICES = [
        ('Apple', 'Apple'),
        ('Samsung', 'Samsung'),
        ('OnePlus', 'OnePlus'),
        ('Xiaomi', 'Xiaomi'),
        ('Realme', 'Realme'),
        ('Vivo', 'Vivo'),
        ('Oppo', 'Oppo'),
        ('Motorola', 'Motorola'),
        ('Nokia', 'Nokia'),
        ('Other', 'Other'),
    ]
    
    distributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', limit_choices_to={'user_type': 'distributor'})
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    model_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    # Pictures
    image1 = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image4 = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Price
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Original price before discount")
    discount = models.IntegerField(default=0, help_text="Discount percentage")
    
    # Features
    features = models.TextField(help_text="Key features of the mobile")
    
    # Specifications
    specifications = models.JSONField(default=dict, help_text="Technical specifications in JSON format")
    
    # Stock
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand} {self.model_name}"
    
    def get_discounted_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price


class Cart(models.Model):
    """Shopping cart model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.model_name} x {self.quantity}"
    
    def get_total_price(self):
        return self.product.get_discounted_price() * self.quantity


class Order(models.Model):
    """Order model for storing order details"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=50, unique=True)
    
    # Delivery Details
    delivery_name = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=10)
    delivery_email = models.EmailField()
    delivery_address = models.TextField()
    delivery_location = models.JSONField(null=True, blank=True, help_text="Live location coordinates")
    
    # Order Details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"XM{timezone.now().strftime('%Y%m%d%H%M%S')}{self.id or ''}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=100)  # Store name at time of order
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def get_total_price(self):
        return self.product_price * self.quantity


class Review(models.Model):
    """Product review model"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.model_name} - {self.rating} stars"


# Utility function to send welcome_email
def send_welcome_email(user):
    from django.core.mail import send_mail
    from django.conf import settings
    
    user_type_text = "Distributor" if user.user_type == 'distributor' else "Customer"
    
    # Get user's name (prefer first_name, fall back to username)
    user_name = user.first_name if user.first_name else user.username
    
    subject = 'Welcome to buyX - Let\'s Start Our Journey Together!'
    message = f'''Dear {user_name},

Thanks for choosing buyX. Let's start our journey together

Best regards,
buyX Team
'''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


# Utility function to send order confirmation email
def send_order_confirmation_email(order):
    from django.core.mail import send_mail
    from django.conf import settings
    
    # Get order items details
    items_list = []
    for item in order.items.all():
        items_list.append(f"- {item.product_name} x {item.quantity} (Rs.{item.product_price})")
    items_details = "\n".join(items_list)
    
    subject = 'Order Confirmed - Your buyX Order'
    message = f'''Dear {order.delivery_name},

Your order has been successfully confirmed. Track your order with the given order id: {order.order_id}

Order Details:
---------------
Order ID: {order.order_id}
Total Amount: Rs.{order.total_amount}

Thank you for shopping with buyX!

Best regards,
buyX Team
'''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.delivery_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


# Utility function to send order SMS
def send_order_sms(phone, order_id, status):
    from django.conf import settings
    
    # Using Twilio (example implementation)
    try:
        import twilio.rest
        
        client = twilio.rest.Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = f"{settings.SITE_NAME}: Your order {order_id} has been {status}. Thank you for shopping with us!"
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=f"+91{phone}"
        )
        return True
    except ImportError:
        print("Twilio not installed. Install with: pip install twilio")
        return False
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False
