from django.urls import path, include
from accounts import views
from accounts.views import *

urlpatterns = [
    path("logout", views.logout, name="logout"),
    path("login", views.login, name="login"),
    path("get_qrcode", views.get_qrcode, name="get_qrcode"),
    path("list", UserListView.as_view(), name="list_user"),
    path("register", views.register, name="register"),
    path("change_password", views.change_password, name="change_password"),
    path('update/<int:pk>', UserUpdateView.as_view(), name='update_user'),
    path('detail/<int:pk>', UserDetailView.as_view(), name='detail_user'),
    path('delete/<int:pk>', UserDeleteView.as_view(), name='delete_user'),
]
