from django.contrib import admin
from .models import User, Distributor, Product, Cart, Order, OrderItem, Review


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'phone', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'phone']


# Custom Admin for Distributors
class DistributorAdmin(admin.ModelAdmin):
    """Admin for managing distributor users"""
    list_display = ['email', 'username', 'phone', 'is_active', 'created_at', 'product_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'username', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['password', 'last_login', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Filter to show only distributor users"""
        queryset = super().get_queryset(request)
        return queryset.filter(user_type='distributor')
    
    def product_count(self, obj):
        """Show number of products added by this distributor"""
        count = Product.objects.filter(distributor=obj).count()
        return count
    product_count.short_description = 'Products'


# Register DistributorAdmin with the Distributor proxy model (not the base User model)
# This allows separate admin interface for distributors
admin.site.register(Distributor, DistributorAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model_name', 'price', 'discount', 'stock', 'is_available', 'created_at']
    list_filter = ['brand', 'is_available', 'created_at']
    search_fields = ['model_name', 'brand']
    prepopulated_fields = {'slug': ('model_name',)}


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'product__model_name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_id', 'user__email']
    readonly_fields = ['order_id', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_price', 'quantity']
    search_fields = ['order__order_id', 'product_name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'product__model_name']
