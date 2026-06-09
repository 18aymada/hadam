import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import FileResponse, HttpResponseForbidden

from .models import Product, Order, OrderItem, DownloadToken

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    products = Product.objects.all()
    return render(request, 'core/home.html', {'products': products})


def staff_only(user):
    return user.is_staff


@login_required
@user_passes_test(staff_only)
def dashboard(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('total'))['total__sum'] or 0
    paid_orders = Order.objects.filter(is_paid=True).count()
    pending_orders = Order.objects.filter(is_paid=False).count()
    recent_orders = Order.objects.order_by('-created_at')[:5]

    return render(request, 'core/dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'paid_orders': paid_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    })


def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def add_to_cart(request, product_id):
    cart = get_cart(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    save_cart(request, cart)
    return redirect('cart')


def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    return redirect('cart')


def cart_view(request):
    cart = get_cart(request)
    products = []
    total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        product.qty = qty
        product.total_price = product.price * qty
        total += product.total_price
        products.append(product)

    return render(request, 'core/cart.html', {
        'products': products,
        'total': total
    })


@login_required
def create_checkout_session(request):
    cart = get_cart(request)

    line_items = []
    total = 0

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {"name": product.title},
                "unit_amount": int(product.price * 100),
            },
            "quantity": qty,
        })

        total += float(product.price) * qty

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/payment-success/?session_id={CHECKOUT_SESSION_ID}'),
        cancel_url=request.build_absolute_uri('/cart/'),
    )

    Order.objects.create(
        user=request.user,
        total=total,
        stripe_session_id=session.id,
        is_paid=False
    )

    return redirect(session.url)


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')

    order = Order.objects.get(stripe_session_id=session_id)
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        order.is_paid = True
        order.save()

        cart = request.session.get('cart', {})

        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=qty
            )

            DownloadToken.objects.create(
                user=request.user,
                product=product
            )

        request.session['cart'] = {}

    return render(request, 'core/success.html', {'order': order})


@login_required
def download_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    token = DownloadToken.objects.filter(
        user=request.user,
        product=product
    ).order_by('-created_at').first()

    if not token:
        return HttpResponseForbidden("No download access")

    if not token.is_valid():
        return HttpResponseForbidden("Download expired (72 hours)")

    return FileResponse(product.file.open(), as_attachment=True)