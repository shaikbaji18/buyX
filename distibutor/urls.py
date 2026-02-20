from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.distributor_signup, name='distributor_signup'),
    path('login/', views.distributor_login, name='distributor_login'),
    path('logout/', views.distributor_logout, name='distributor_logout'),
    path('dashboard/', views.distributor_dashboard, name='distributor_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.distributor_orders, name='distributor_orders'),
    path('update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
