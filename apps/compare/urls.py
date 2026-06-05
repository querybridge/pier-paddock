from django.urls import path

from . import views

app_name = "compare"

urlpatterns = [
    path("", views.CompareView.as_view(), name="index"),
    path("add/<int:pk>/", views.add, name="add"),
    path("remove/<int:pk>/", views.remove, name="remove"),
    path("clear/", views.clear, name="clear"),
]
