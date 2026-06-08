"""Operator Console URLs (staff-gated). Fully built in console.py."""
from django.urls import path

from . import console

app_name = "console"

urlpatterns = [
    path("", console.DashboardView.as_view(), name="dashboard"),
    path("members/", console.MembersView.as_view(), name="members"),
    path("members/<int:pk>/", console.MemberDetailView.as_view(), name="member"),
    path("early-access/", console.EarlyAccessView.as_view(), name="early_access"),
    path("config/", console.ConfigView.as_view(), name="config"),
]
