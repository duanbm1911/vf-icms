from django.urls import path, include
from accounts import views
from accounts.views import *

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("logout", views.logout, name="logout"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("list-users", UserListView.as_view()),
    path("change_password", views.change_password, name="change_password"),
    path("get_qrcode", views.get_qrcode, name="get_qrcode"),
]
