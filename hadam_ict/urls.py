from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from core import views


urlpatterns = [
    # ======================
    # ADMIN
    # ======================
    path('admin/', admin.site.urls),

    # ======================
    # CORE PAGES
    # ======================
    path('', views.home, name='home'),

    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),

    # ======================
    # PAYMENT FLOW
    # ======================
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # Stripe webhook (VERY IMPORTANT)
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),

    # ======================
    # USER AREA
    # ======================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ======================
    # DOWNLOAD SYSTEM
    # ======================
    path('download/<int:id>/', views.download_product, name='download_product'),

    # ======================
    # AUTH
    # ======================
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
]