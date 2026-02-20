from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('accounts/login/', views.user_login, name='account_login'),
    path('logout/', views.logout_view, name='logout'),
    path('shopping/', views.shopping, name='shopping'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-buy-now/', views.checkout_buy_now, name='checkout_buy_now'),
    path('payment-options/<str:order_id>/', views.payment_options, name='payment_options'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.orders, name='orders'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
]
