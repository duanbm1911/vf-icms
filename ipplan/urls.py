from django.urls import path
from ipplan import views
from ipplan.views import *


urlpatterns = [
    path("create-location", LocationCreateView.as_view(), name="create_location"),
    path("create-region", RegionCreateView.as_view(), name="create_region"),
    path("create-subnet", SubnetCreateView.as_view(), name="create_subnet"),
    path("create-subnet-group", SubnetGroupCreateView.as_view(), name="create_subnet_group"),
    path("create-multiple-subnet", views.create_multiple_subnet, name="create_multiple_subnet"),
    path("list-subnet", SubnetListView.as_view(), name="list_subnet"),
    path("delete-subnet/<int:pk>", SubnetDeleteView.as_view(), name="delete_subnet"),
    path("request-ip", views.request_ip_form, name="request_ip"),
    path("request-multiple-ip", views.request_multiple_ip, name="request_multiple_ip"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("list-subnet-tree", views.list_subnet_tree, name="list_subnet_tree"),
    path("list-ip/<int:pk>", views.list_ip, name="list-ip"),
    path("update-subnet/<int:pk>", SubnetUpdateView.as_view(), name="update_subnet"),
    path("list-ip/<int:pk>/delete-ip/<int:id>", IpAddressModelDeleteView.as_view(), name="delete_ip"),
    path("list-ip/<int:pk>/update-ip/<int:id>", IpAddressModelUpdateView.as_view(), name="update_ip"),
    path("list-ip/<int:pk>/detail-ip/<int:id>", IpAddressModelDetailView.as_view(), name="detail_ip"),
    path("list-region", RegionListView.as_view(), name="list_region"),
    path("list-subnet-group", SubnetGroupListView.as_view(), name="list_subnet_group"),
    path("list-location", LocationListView.as_view(), name="list_location"),
    path("update-region/<int:pk>", RegionUpdateView.as_view(), name="update_region"),
    path("delete-region/<int:pk>", RegionDeleteView.as_view(), name="delete_region"),
    path("update-location/<int:pk>", LocationUpdateView.as_view(), name="update_location"),
    path("delete-location/<int:pk>", LocationDeleteView.as_view(), name="delete_location"),
    path("update-subnet-group/<int:pk>", SubnetGroupUpdateView.as_view(), name="update_subnet_group"),
    path("delete-subnet-group/<int:pk>", SubnetGroupDeleteView.as_view(), name="delete_subnet_group"),
    path("ipplan-export", views.ipplan_export, name="ipplan_export"),
]
