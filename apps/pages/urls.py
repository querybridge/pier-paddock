from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
