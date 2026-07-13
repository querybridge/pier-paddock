# Demo → Production Checklist

This site currently runs in **demo mode**: it is deliberately **not indexable**, checkout is
**disabled at the final step**, and external integrations are **built but inactive**. Everything
here must be reviewed/changed before a real production launch — a fully **SEO/AI-discoverable**
and **user-shoppable** site.

> **Maintaining this file:** it is a *living* document. Whenever a **demo-only** feature or an
> intentionally-inactive seam is added, add a line here (with the file/flag that controls it) so
> nothing is missed at launch. Don't delete items on launch — check them off.

Trigger phrase: when the owner says **"shift into full production"**, work through this list
(confirm the real domain, payment provider and brand name first).

---

## 1. SEO / AI discoverability (currently deliberately `noindex`)

- [ ] **Storefront `noindex` → `index`.** Site-wide default is `{% block robots %}<meta
  name="robots" content="noindex, follow">{% endblock %}` in `templates/oscar/base.html`. Decide
  per-surface index policy (home, shop browse, category, PDP) and keep cart/checkout/account noindex.
- [ ] **PDPs indexable.** The AI-discovery layer is already built (FAQ section + Product/Offer/
  FAQPage/BreadcrumbList JSON-LD + OpenGraph/Twitter/price meta — `apps/shop/seo.py`, `shop_seo`
  tags, `partials/_pdp_seo.html` + `_pdp_faq.html`) but kept noindex. Re-enable by overriding the
  robots block in `templates/oscar/catalogue/detail.html` with
  `index, follow, max-image-preview:large` (there's a comment marking the spot).
- [ ] **Product/category sitemap.** `/sitemap.xml` currently covers the **Wagtail magazine only**.
  Add an Oscar product + category sitemap (`django.contrib.sitemaps`, already installed) and serve a
  **sitemap index** combining it with the magazine sitemap; reference it in `robots.txt`.
- [ ] **Real host / absolute URLs.** Set `WAGTAILADMIN_BASE_URL`, `LIFESTYLE_BASE_URL`, and the
  `django.contrib.sites` Site domain to the production host so canonical/feed/JSON-LD URLs are correct.
- [ ] **Magazine search backend.** Swap the SQLite substring search (`apps/lifestyle/views.py`
  `magazine_search`) for a real backend (Postgres FTS / Elasticsearch) for relevance + stemming.
- [ ] **Owner placeholders** (empty by default): `GA4_MEASUREMENT_ID`, `INDEXNOW_KEY` (+ serve
  `/<key>.txt`), `LIFESTYLE_OG_DEFAULT_IMAGE` (1200×630). robots.txt already welcomes AI crawlers.

## 2. Commerce — make it user-shoppable (checkout disabled)

- [ ] **Enable real checkout.** `apps/checkout` is a fork with **payments disabled at place-order**.
  Integrate a real gateway (Stripe/Adyen/…), allow order creation, remove the "payments are disabled
  in this demo" notice.
- [ ] **Loyalty from real orders.** Tier progression / Retailer's Credit is driven by the Operator
  Console "Simulate purchase" in the demo. Wire real order signals to `Membership.recompute()`.
- [ ] **Merchant XML feed.** `apps/merchant` feed fetch/upsert is simulated ("Sync now" is inert) —
  wire the real feed parse + product upsert.

## 3. Integrations (built as inactive seams)

- [ ] **SendGrid** (transactional email) — add keys, flip `LOYALTY_TRANSACTIONAL_ENABLED`.
- [ ] **Mailchimp** (marketing / magazine newsletter) — add `MAILCHIMP_*` keys, flip
  `LOYALTY_MARKETING_ENABLED`, then `manage.py sync_pending_subscribers` (magazine sign-ups queue
  locally as `PendingSubscriber`).
- [ ] **Revive Adserver** (magazine ad zones) — set `REVIVE_ENABLED` + Revive tags. Ad zones are the
  Revive user's domain, not the CMS editor (the `editor@pierpaddock.demo` account has no AdZone perms
  by design).

## 4. Content & branding (placeholders)

- [ ] **Brand name/tagline** are placeholders — `BRAND_NAME` / `BRAND_TAGLINE` in `config/settings.py`
  (single source; re-brands everywhere). Set the real brand.
- [ ] **Remove demo framing** — `BRAND_DEMO_DISCLAIMER` banners, "Demo site — transactions are not
  active" notices, README "not a production site" language.
- [ ] **Fulfilment partner** — `BRAND_FULFILMENT_PARTNER` / footer attribution (currently IDC stand-in).

## 5. Security & infrastructure hardening

- [ ] `DJANGO_DEBUG=0`, real `SECRET_KEY`, locked `DJANGO_ALLOWED_HOSTS`, HTTPS/HSTS, secure cookies.
- [ ] **Remove/secure the seeded demo accounts** (known passwords) — admin, the five Crest tier
  members, operator, merchant, `editor@pierpaddock.demo`.
- [ ] **Database** — move off the committed **SQLite** to a managed DB.
- [ ] **Media** — magazine renditions are currently committed to git (so the demo renders without
  regeneration); production may prefer on-demand generation + writable media on real storage/CDN.
  Serve `/media/` and `/static/` via CDN.

---

## Demo-only features log (add as we build)

_Newest first. Each entry: what's demo-only, and the switch to review at launch._

- **2026-07-13 — PDP AI-discovery layer kept `noindex`.** PDPs have full FAQ + JSON-LD + meta but
  inherit the site-wide noindex; flip via the robots block in `oscar/catalogue/detail.html`. (§1)
- **(baseline) — Whole storefront `noindex`** (`oscar/base.html` robots block). (§1)
- **(baseline) — Checkout disabled** at place-order (`apps/checkout` fork). (§2)
- **(baseline) — SendGrid / Mailchimp / Revive** integrations inactive. (§3)
- **2026-07-13 — Committed sorl thumbnail cache (`media/cache/`) + empty-KVStore invariant.**
  Shop/magazine product thumbnails are committed so they render on deploy without regeneration.
  The committed db's sorl **KVStore must stay empty** — run `manage.py clean_thumbnails` before
  `git add db.sqlite3` (a populated KVStore ships stale cache pointers → broken images). Prod:
  regenerate on real storage/CDN. (§5)
- **(baseline) — Committed SQLite + committed Wagtail renditions + seeded demo accounts.** (§5)
