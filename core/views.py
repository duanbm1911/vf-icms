from django.shortcuts import render
from django.shortcuts import redirect


# Create your views here.

def redirect_home_url(request):
    return redirect("device_dashboard")


def error_404(request, exception):
    return redirect("device_dashboard")