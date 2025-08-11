from django.urls import path
from core import views
from django.conf.urls import handler400
from core.views import *


handler400 = views.error_404

urlpatterns = [
    path("", views.redirect_home_url),
]
