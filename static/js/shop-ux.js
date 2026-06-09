/* Shop UX: mini-cart drawer, quick-view modal, mobile filter drawer.
   Progressive enhancement — every action has a no-JS fallback (real links/forms). */
(function () {
    "use strict";

    function cookie(name) {
        var m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
        return m ? m.pop() : "";
    }
    function setCartCount(n) {
        document.querySelectorAll(".js-cart-count").forEach(function (el) { el.textContent = n; });
    }

    /* ---------------- Filter drawer (PLP, mobile) ---------------- */
    window.ppOpenFilters = function () {
        var s = document.getElementById("ppShopSidebar"), b = document.getElementById("ppFilterBackdrop");
        if (s) s.classList.add("open"); if (b) b.classList.add("open");
        document.body.style.overflow = "hidden";
    };
    window.ppCloseFilters = function () {
        var s = document.getElementById("ppShopSidebar"), b = document.getElementById("ppFilterBackdrop");
        if (s) s.classList.remove("open"); if (b) b.classList.remove("open");
        document.body.style.overflow = "";
    };

    /* ---------------- Mini-cart drawer ---------------- */
    window.ppOpenCart = function () {
        var d = document.getElementById("ppMiniCart"), b = document.getElementById("ppMiniCartBackdrop");
        if (d) d.classList.add("open"); if (b) b.classList.add("open");
        document.body.style.overflow = "hidden";
    };
    window.ppCloseCart = function () {
        var d = document.getElementById("ppMiniCart"), b = document.getElementById("ppMiniCartBackdrop");
        if (d) d.classList.remove("open"); if (b) b.classList.remove("open");
        var added = document.getElementById("ppMiniAdded"); if (added) added.textContent = "";
        document.body.style.overflow = "";
    };

    /* ---------------- Quick view modal ---------------- */
    window.ppCloseQuickView = function () {
        var m = document.getElementById("ppQuickView"); if (m) m.classList.remove("open");
        document.body.style.overflow = "";
    };
    window.ppQVBackdrop = function (e) {
        if (e.target && e.target.id === "ppQuickView") { window.ppCloseQuickView(); }
    };

    /* ---------------- Intercept add-to-cart forms ---------------- */
    function pkFromAction(action) {
        var m = action && action.match(/\/basket\/add\/(\d+)\//);
        return m ? m[1] : null;
    }

    document.addEventListener("submit", function (e) {
        var form = e.target;
        if (!form || form.tagName !== "FORM") return;
        var pk = pkFromAction(form.getAttribute("action") || "");
        if (!pk) return;                       // not a basket-add form — leave it alone
        e.preventDefault();
        var qtyInput = form.querySelector("[name=quantity]");
        var qty = qtyInput ? qtyInput.value : 1;
        var token = (form.querySelector("[name=csrfmiddlewaretoken]") || {}).value || cookie("csrftoken");
        var fd = new FormData();
        fd.append("quantity", qty);
        fd.append("csrfmiddlewaretoken", token);
        var btn = form.querySelector("button[type=submit]");
        if (btn) btn.disabled = true;
        fetch("/shop/cart/add/" + pk + "/", {
            method: "POST",
            headers: { "X-CSRFToken": token, "X-Requested-With": "XMLHttpRequest" },
            body: fd, credentials: "same-origin"
        })
            .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
            .then(function (data) {
                if (btn) btn.disabled = false;
                if (!data.ok) { form.submit(); return; }
                setCartCount(data.num_items);
                var body = document.getElementById("ppMiniCartBody");
                if (body) body.innerHTML = data.drawer_html;
                var added = document.getElementById("ppMiniAdded");
                if (added && data.added) { added.textContent = " · Added " + (data.added.model || "item"); }
                window.ppCloseQuickView();
                window.ppOpenCart();
            })
            .catch(function () { if (btn) btn.disabled = false; form.submit(); });  // fallback
    });

    /* ---------------- Quick-view triggers ---------------- */
    document.addEventListener("click", function (e) {
        var t = e.target.closest ? e.target.closest(".pp-quickview-trigger") : null;
        if (!t) return;
        var pk = t.getAttribute("data-pk");
        if (!pk) return;
        e.preventDefault();
        var modal = document.getElementById("ppQuickView"), body = document.getElementById("ppQuickViewBody");
        if (!modal || !body) { window.location = t.href; return; }
        body.innerHTML = '<div class="pp-qv-loading">Loading…</div>';
        modal.classList.add("open");
        document.body.style.overflow = "hidden";
        fetch("/shop/quickview/" + pk + "/", { credentials: "same-origin" })
            .then(function (r) { return r.ok ? r.text() : Promise.reject(r); })
            .then(function (html) { body.innerHTML = html; })
            .catch(function () { window.location = t.href; });
    });

    /* ---------------- Header cart icon opens the drawer ---------------- */
    document.addEventListener("click", function (e) {
        var c = e.target.closest ? e.target.closest(".js-cart-toggle") : null;
        if (!c) return;
        e.preventDefault();
        window.ppOpenCart();
    });

    /* ---------------- Escape closes overlays ---------------- */
    document.addEventListener("keyup", function (e) {
        if (e.key === "Escape") { window.ppCloseCart(); window.ppCloseFilters(); window.ppCloseQuickView(); }
    });

    /* ---------------- Pad body when a sticky buy bar is present ---------------- */
    if (document.querySelector(".pp-buybar")) { document.body.classList.add("pp-has-buybar"); }
})();
