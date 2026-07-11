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

## Phase 1 — iNews template intake & rebrand — 2026-07-11 ✅

**Built**
- Copied the iNews assets (css/js/img/webfonts + root `style.css`) into
  `apps/lifestyle/static/lifestyle/` (namespaced; ~2.1 MB). Skipped the `sass/`
  source.
- **Base templates** in `apps/lifestyle/templates/lifestyle/`: `base.html` (the
  full magazine chrome), `index.html` (Home 3 landing base), `article_base.html`,
  `category_base.html`, `404.html`, `search.html`, `advertise.html`. The Wagtail
  landing page template now extends `index.html`.
- **Rebrand:** SVG text-mark logo `pp-lifestyle-logo.svg` (navy serif "Pier &
  Paddock", gold rule, gold "LIFESTYLE"), 270×74 to preserve layout; favicon →
  `crest.ico`; footer credit + `<title>` rebranded; iNews red accent recoloured to
  the P&P palette via `pp-lifestyle.css`.
- **Ad zones:** `AdZone` snippet (slug/name/dims/target/placeholder/`revive_tag`)
  + `{% ad_zone "slug" %}` tag (renders local placeholder, or the Revive tag when
  `REVIVE_ENABLED`). `lifestyle_ads` command generates #666 "Your Ad Here"
  placeholders and seeds the zones.
- **Primary nav:** data-driven `{% lifestyle_nav %}` → Fashion, Motorsports,
  Watersports, Business, Entertainment, Health (fixed fallback until Phase 2
  CategoryPages exist), + **Shop** → `/`.
- **Footer:** the iNews magazine footer, then the **shared zwat storefront footer**
  (`{% include "oscar/partials/_footer.html" %}`) stacked below it.

**Ad slot inventory** (dimensions from the template's ad images)
| Zone slug | Placement | Size |
|---|---|---|
| `leaderboard_top` | logo bar | 730×95 |
| `in_content` | between blocks | 730×95 |
| `footer` | magazine footer widget | 730×95 |
| `sidebar` | article sidebar | 350×350 |

**Files touched**
- `apps/lifestyle/models.py` (AdZone), `migrations/0002_adzone.py`,
  `templatetags/lifestyle_tags.py`, `management/commands/lifestyle_ads.py`,
  `views.py`, `templates/lifestyle/*`, `static/lifestyle/*`
- `config/urls.py` (advertise stub), `db.sqlite3` (AdZone rows)

**Deviations**
- The `/advertise/` page is a Phase-1 **stub** (magazine skin) so nav/footer links
  resolve; the full form is Phase 5.
- The stacked P&P footer is styled by a small `pp-lifestyle.css` block (the zwat
  theme CSS isn't loaded on the magazine to avoid two full frameworks colliding);
  it reads as intentional. Refine in Phase 7 if desired.
- The nav search box posts to `/lifestyle/search/` (built in Phase 7).

**Verify (all pass)**
- `/lifestyle/` → 200 with the rebranded logo, correct nav, placeholder ads,
  magazine footer + stacked P&P footer; every `/static/lifestyle/*` asset → 200.
- No visible "iNews" branding. `/advertise/` stub → 200. `check` clean.
- Screenshot confirmed the rebrand (navy/gold logo, dark stacked storefront footer).

**Deploy note:** add `python manage.py lifestyle_ads` after `migrate` +
`lifestyle_bootstrap` (idempotent; generates ad placeholders + seeds zones).

---

## Ad-hoc / early items

- **2026-07-11 — Storefront primary nav "Blog" → "Lifestyle"** (a Phase 7 item,
  done early at the owner's request). Both the desktop and mobile menus in
  `templates/oscar/partials/_header.html` now link to `/lifestyle/`. The footer
  "Journal" link is untouched for now.

---

## Owner (Mike) — outstanding placeholders

| Placeholder | Status | Notes |
|---|---|---|
| iNews `TEMPLATE_DIR` | ✅ present | `/Users/querybridge/envs/idcwatch/inews_396ccbc46b5d2d6840665ca80b82bc68` — Phase 1 unblocked |
| `MAILCHIMP_API_KEY` / `MAILCHIMP_LIST_ID` | ⏳ pending | settings constants, empty; subs stored locally (Phase 5) |
| Revive Adserver endpoint | ⏳ pending | `REVIVE_ENABLED=False`; local placeholder creatives (Phase 1/4) |
| GA4 / Search Console IDs | ⏳ pending | `GA4_MEASUREMENT_ID` empty (Phase 6) |
