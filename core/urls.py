from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('cart/', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.create_checkout_session, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),

    path('download/<int:product_id>/', views.download_product, name='download_product'),
]