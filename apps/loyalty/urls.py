from django.urls import path

from . import views

app_name = "loyalty"

urlpatterns = [
    path("membership/", views.MembershipDashboardView.as_view(), name="dashboard"),
    path("grail/", views.GrailListView.as_view(), name="grail"),
    path("grail/<int:pk>/remove/", views.GrailDeleteView.as_view(), name="grail_remove"),
    path("alerts/", views.AlertsView.as_view(), name="alerts"),
    path("reports/<int:pk>/", views.MarketReportView.as_view(), name="report"),
]
# NB: the Vault (apps.vault.urls) is mounted at /account/vault/ in config/urls
# at the TOP level so its namespace stays 'vault' (not nested under 'loyalty').
