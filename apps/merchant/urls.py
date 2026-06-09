from django.urls import path

from . import views

app_name = "merchant"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("listings/", views.ListingsView.as_view(), name="listings"),
    path("feed/", views.FeedView.as_view(), name="feed"),
    path("sales/", views.SalesView.as_view(), name="sales"),
]
