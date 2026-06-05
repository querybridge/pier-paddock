from django.urls import path

from . import views

app_name = "vault"

urlpatterns = [
    path("", views.VaultView.as_view(), name="index"),
    path("add/<int:pk>/", views.add, name="add"),
    path("own/<int:pk>/", views.mark_owned, name="mark_owned"),
    path("remove/<int:pk>/", views.remove, name="remove"),
]
