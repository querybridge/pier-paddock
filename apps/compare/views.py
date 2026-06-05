"""Session-based watch comparison (up to 3 watches, no login required)."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from oscar.core.loading import get_model

Product = get_model("catalogue", "Product")

SESSION_KEY = "compare_ids"
MAX_COMPARE = 3

# (attribute code, display label) in the order shown on the compare table.
SPEC_ATTRS = [
    ("brand", "Brand"),
    ("reference", "Reference Number"),
    ("case_material", "Case Material"),
    ("case_size", "Case Size"),
    ("movement", "Movement"),
    ("dial_color", "Dial Color"),
    ("bracelet", "Bracelet / Strap"),
    ("water_resistance", "Water Resistance"),
    ("condition", "Condition"),
    ("year", "Year"),
    ("box_papers", "Box & Papers"),
]


def _ids(request):
    return list(request.session.get(SESSION_KEY, []))


def _save(request, ids):
    request.session[SESSION_KEY] = ids
    request.session.modified = True


def add(request, pk):
    get_object_or_404(Product, pk=pk)
    ids = _ids(request)
    if pk in ids:
        pass
    elif len(ids) >= MAX_COMPARE:
        messages.info(
            request,
            "You can compare up to %d watches — remove one to add another."
            % MAX_COMPARE,
        )
    else:
        ids.append(pk)
        _save(request, ids)
    return redirect("compare:index")


def remove(request, pk):
    ids = _ids(request)
    if pk in ids:
        ids.remove(pk)
        _save(request, ids)
    return redirect("compare:index")


def clear(request):
    _save(request, [])
    return redirect("compare:index")


class CompareView(TemplateView):
    template_name = "compare/compare.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ids = _ids(self.request)
        products = list(
            Product.objects.filter(id__in=ids).prefetch_related(
                "attribute_values__attribute", "images", "stockrecords"
            )
        )
        products.sort(key=lambda p: ids.index(p.id))

        attr_maps = []
        for p in products:
            attr_maps.append(
                {av.attribute.code: av.value_as_text for av in p.attribute_values.all()}
            )

        rows = []
        for code, label in SPEC_ATTRS:
            rows.append(
                {"label": label, "values": [m.get(code, "—") for m in attr_maps]}
            )

        ctx["compare_products"] = products
        ctx["compare_rows"] = rows
        ctx["can_add_more"] = len(products) < MAX_COMPARE
        ctx["max_compare"] = MAX_COMPARE
        return ctx
