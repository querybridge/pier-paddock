from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from oscar.apps.customer.forms import EmailAuthenticationForm
from oscar.core.loading import get_model

from .operations import operations_home_url

Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")


class HomeView(TemplateView):
    """Skinned homepage (zwat 'Home Page 3')."""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        browsable = (
            Product.objects.browsable()
            .filter(structure__in=[Product.STANDALONE, Product.PARENT])
            .order_by("-date_created")
        )

        ctx["new_arrivals"] = list(browsable[:8])
        # "Featured" — a stable but distinct slice for the carousel.
        ctx["featured_products"] = list(browsable.order_by("title")[:8])

        # Top-level brand/style categories for the collection blocks.
        ctx["collections"] = list(Category.get_root_nodes()[:6])

        try:
            from apps.blog.models import Post

            ctx["latest_posts"] = list(
                Post.objects.filter(published=True).order_by("-date")[:3]
            )
        except Exception:
            ctx["latest_posts"] = []

        return ctx


class OperationsLoginView(View):
    """A single staff sign-in page ("Operations"). On success, routes the user
    to the right back-office by role: merchants -> Merchant Portal, operators /
    superusers -> Operator Console. A ?next pointing at the user's own area is
    honoured so deep links survive the login."""

    template_name = "operations/login.html"

    def get(self, request, *args, **kwargs):
        # Already signed in? Send them straight to where they belong.
        if request.user.is_authenticated:
            return redirect(self._destination(request, request.user))
        return render(request, self.template_name, {"next": request.GET.get("next", "")})

    def post(self, request, *args, **kwargs):
        form = EmailAuthenticationForm(host=request.get_host(), data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(self._destination(request, user))
        return render(
            request, self.template_name,
            {"form": form, "next": request.POST.get("next", ""), "error": True},
        )

    def _destination(self, request, user):
        from apps.merchant.models import is_merchant

        nxt = request.POST.get("next") or request.GET.get("next") or ""
        if nxt.startswith("/merchant/") and is_merchant(user):
            return nxt
        if nxt.startswith("/console/") and user.is_staff and not is_merchant(user):
            return nxt
        # No (valid) next — route by role.
        return operations_home_url(user) or "/"
