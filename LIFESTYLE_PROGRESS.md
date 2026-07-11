# LIFESTYLE_PROGRESS.md

Running log for building **Pier & Paddock Lifestyle** (Wagtail magazine) per
`LIFESTYLE_MAGAZINE.md`. Read this before starting any session. Append a section
per phase: what was built, files touched, deviations, and owner placeholders.

Wagtail CMS admin: **`/cms-admin/`** (log in as a superuser — `admin@example.com` /
`Admin1234!`). The magazine serves under **`/lifestyle/`**.

---

## Phase 0 — Wagtail installation & wiring — 2026-07-11 ✅

**Built**
- Installed **Wagtail 7.4.2** (first series supporting Django 5.2). Added to
  `requirements.txt`.
- New app **`apps/lifestyle/`** with a stub **`LifestyleIndexPage`** (Wagtail
  `Page`, `max_count=1`) + a plain stub template.
- Wired Wagtail into `config/settings.py` (INSTALLED_APPS, `RedirectMiddleware`,
  the `wagtail.contrib.settings` context processor, `WAGTAIL_*` config, WebP
  rendition conversions, DB search backend, and empty GA4/Revive/Mailchimp
  seams).
- Wired `config/urls.py`: `/cms-admin/` (Wagtail admin), `/documents/`,
  `/lifestyle/` (all CMS pages), and the `/blog/* → /lifestyle/*` 301 redirect.
- `manage.py lifestyle_bootstrap` (idempotent) creates the landing page and
  points the default Wagtail Site at it, so it serves at `/lifestyle/`.

**Files touched**
- `apps/lifestyle/{__init__,apps,models}.py`,
  `apps/lifestyle/migrations/0001_initial.py`,
  `apps/lifestyle/management/commands/lifestyle_bootstrap.py`,
  `apps/lifestyle/templates/lifestyle/lifestyle_index_page.html`
- `config/settings.py`, `config/urls.py`, `requirements.txt`
- `db.sqlite3` (Wagtail schema + landing page; thumbnail KVStore left empty)

**Deviations from spec** (per rule #5 — prefer codebase conventions, record here)
1. The app lives at **`apps/lifestyle/`** (this repo keeps all custom apps under
   `apps/`), not a bare `lifestyle/`. Templates/static are still namespaced under
   `lifestyle/`.
2. **`/blog/` conflict:** the existing `apps.blog` journal owned `/blog/` and is
   linked from the *protected* zwat nav/footer via `{% url 'blog:list' %}`. To
   satisfy the spec's `/blog/ → /lifestyle/` 301 **without** editing zwat
   templates or breaking `reverse()`, the redirect is registered *before* the
   `apps.blog` include: all `/blog/*` requests 301 to `/lifestyle/*`, while the
   `blog:` URL names still resolve. The old journal is effectively retired.
   (Storefront nav/footer link relabeling happens in Phase 7.)
3. The site root is created by the idempotent **`lifestyle_bootstrap`** command
   rather than a data migration (manipulating the Wagtail page tree via historical
   models is fragile).

**Verify (all pass)**
- Store unaffected: `/`, `/shop/`, `/membership/` → 200.
- `/cms-admin/` → 302 to Wagtail login. `/lifestyle/` → 200 stub.
- `/blog/` → 301 `/lifestyle/`; `/blog/some-post/` → 301 `/lifestyle/some-post/`.
- `reverse('blog:list')` still resolves (zwat templates safe).
- `python manage.py check` → no issues.

**Deploy note:** after pulling, run `python manage.py migrate` **and**
`python manage.py lifestyle_bootstrap` (both idempotent). The committed
`db.sqlite3` already has the Wagtail schema + landing page.

---

## Owner (Mike) — outstanding placeholders

| Placeholder | Status | Notes |
|---|---|---|
| iNews `TEMPLATE_DIR` | ✅ present | `/Users/querybridge/envs/idcwatch/inews_396ccbc46b5d2d6840665ca80b82bc68` — Phase 1 unblocked |
| `MAILCHIMP_API_KEY` / `MAILCHIMP_LIST_ID` | ⏳ pending | settings constants, empty; subs stored locally (Phase 5) |
| Revive Adserver endpoint | ⏳ pending | `REVIVE_ENABLED=False`; local placeholder creatives (Phase 1/4) |
| GA4 / Search Console IDs | ⏳ pending | `GA4_MEASUREMENT_ID` empty (Phase 6) |
