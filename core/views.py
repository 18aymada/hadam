import stripe

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    FileResponse
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from .models import Product, Purchase


# ======================
# HOME
# ======================

def home(request):
    products = Product.objects.all()

    return render(
        request,
        "home.html",
        {
            "products": products
        }
    )


# ======================
# CART
# ======================

def add_to_cart(request, id):

    cart = request.session.get("cart", [])

    if id not in cart:
        cart.append(id)

    request.session["cart"] = cart

    return redirect("cart")



def cart(request):

    cart_ids = request.session.get("cart", [])

    products = Product.objects.filter(
        id__in=cart_ids
    )

    return render(
        request,
        "cart.html",
        {
            "products": products
        }
    )



def remove_from_cart(request, id):

    cart = request.session.get("cart", [])

    if id in cart:
        cart.remove(id)

    request.session["cart"] = cart

    return redirect("cart")



# ======================
# STRIPE CHECKOUT
# ======================

def checkout(request):

    cart_ids = request.session.get(
        "cart",
        []
    )

    products = Product.objects.filter(
        id__in=cart_ids
    )


    stripe.api_key = settings.STRIPE_SECRET_KEY


    line_items = []


    for product in products:

        line_items.append({

            "price_data": {

                "currency": "usd",

                "product_data": {

                    "name": product.name

                },

                "unit_amount":
                    int(product.price * 100),

            },

            "quantity": 1,

        })


    session = stripe.checkout.Session.create(

        payment_method_types=[

            "card"

        ],

        line_items=line_items,

        mode="payment",


        success_url=request.build_absolute_uri(
            "/payment-success/"
        ),


        cancel_url=request.build_absolute_uri(
            "/cart/"
        ),


        metadata={

            "user_id":
                str(request.user.id),


            "cart_ids":
                ",".join(
                    map(str, cart_ids)
                )

        }

    )


    return redirect(
        session.url
    )



# ======================
# PAYMENT SUCCESS
# ======================

def payment_success(request):

    return render(
        request,
        "payment_success.html"
    )



# ======================
# STRIPE WEBHOOK
# ======================

@csrf_exempt
def stripe_webhook(request):

    payload = request.body

    sig_header = request.META.get(
        "HTTP_STRIPE_SIGNATURE"
    )


    stripe.api_key = (
        settings.STRIPE_SECRET_KEY
    )


    try:

        event = stripe.Webhook.construct_event(

            payload,

            sig_header,

            settings.STRIPE_WEBHOOK_SECRET

        )


    except Exception:

        return HttpResponse(
            status=400
        )



    if event["type"] == "checkout.session.completed":


        session = event["data"]["object"]


        user_id = session["metadata"]["user_id"]

        cart_ids = session["metadata"]["cart_ids"]



        user = User.objects.get(
            id=user_id
        )



        for product_id in cart_ids.split(","):


            product = Product.objects.get(
                id=product_id
            )


            Purchase.objects.get_or_create(

                user=user,

                product=product,

                stripe_session_id=session["id"]

            )



    return HttpResponse(
        status=200
    )



# ======================
# DASHBOARD
# ======================

@login_required
def dashboard(request):

    purchases = Purchase.objects.filter(
        user=request.user
    )


    return render(

        request,

        "dashboard.html",

        {

            "purchases": purchases

        }

    )



# ======================
# SECURE DOWNLOAD
# ======================

@login_required
def download_product(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )


    try:

        purchase = Purchase.objects.get(

            user=request.user,

            product=product

        )



        if not purchase.is_active():

            return HttpResponseForbidden(
                "Download expired"
            )



        if not product.file:

            return HttpResponseForbidden(
                "No file available"
            )



        return FileResponse(

            product.file.open(),

            as_attachment=True

        )


    except Purchase.DoesNotExist:


        return HttpResponseForbidden(
            "You did not purchase this product"
        )



# ======================
# REGISTER
# ======================

def register(request):

    return render(
        request,
        "register.html"
    )



# ======================
# LOGOUT
# ======================

def user_logout(request):

    logout(request)

    return redirect(
        "home"
    )