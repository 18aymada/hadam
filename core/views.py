from django.shortcuts import render
import os
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

def home(request):
    return render(request, "home.html")