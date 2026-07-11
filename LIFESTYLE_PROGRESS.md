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

## Phase 2 — Page models & information architecture — 2026-07-11 ✅

**Built**
- Page models (`apps/lifestyle/models.py`): **CategoryPage** (intro, hero, accent,
  featured curation slots via `CategoryFeatured`, paginated reverse-chron listing),
  **ArticlePage** (post_type, subtitle, hero+alt/caption/credit, authors M2M,
  publish/updated dates, auto `reading_time`, taggit tags, `is_sponsored`,
  `related_products` inline ×4, `related_articles` manual+auto, StreamField `body`
  [minimal — expanded in Phase 3], SEO promote panels: canonical/og_image/noindex),
  **AuthorIndexPage** + **AuthorPage** (portrait, role, bio, socials, article list).
- IA enforced via `parent_page_types`/`subpage_types`; URLs are exactly
  `/lifestyle/<category>/<slug>/`. Expanded `LifestyleIndexPage` to render the
  Home 3 layout (featured hero, trending, latest grid, per-category rails, ads).
- Templates: `article_page`, `category_page`, `author_index_page`, `author_page`,
  a reusable `includes/_article_card.html`, and the wired `index.html`. Phase 2 CSS
  appended to `pp-lifestyle.css`.
- **Seed** `load_lifestyle_demo`: 3 authors, 6 categories, 12 articles across every
  post_type, with generated category-coloured hero images, tags, shoppable Oscar
  products on watch stories, and a sponsored (Partner Content) piece.

**Files touched**
- `apps/lifestyle/models.py`, `migrations/0003_*.py`,
  `management/commands/load_lifestyle_demo.py`, `templates/lifestyle/*`,
  `static/lifestyle/pp-lifestyle.css`
- `.gitignore` (Wagtail renditions), `db.sqlite3` + `media/original_images/`
  (magazine content ships so the demo renders without a reseed)

**Deviations**
- Magazine demo *content* ships in `db.sqlite3` + `media/original_images/` (21
  small placeholders, ~208 KB) so `/lifestyle/` is populated out of the box —
  consistent with how the store ships a runnable db. `load_lifestyle_demo` rebuilds
  it; Wagtail renditions regenerate on demand (gitignored).
- `related_products` uses an Orderable inline (Oscar Product FK); `authors` and
  `related_articles` are ParentalManyToMany.

**Verify (all pass)**
- Full tree navigable: `/lifestyle/` (Home 3 with featured/trending/rails/latest),
  `/lifestyle/<category>/` (hub + pagination), `/lifestyle/<category>/<slug>/`
  (article, exact URL), `/lifestyle/authors/`, `/lifestyle/authors/<slug>/`.
- Article renders h1/byline/body/badge; sponsored → "Partner Content" band;
  watch stories show shoppable "From the Shop" cards + related reading.
- Screenshot confirmed the Home 3 layout (featured hero, numbered trending,
  post-type badges over category-coloured heroes). `check` clean.

**Deploy note:** after `migrate` + `lifestyle_bootstrap` + `lifestyle_ads`, run
`python manage.py load_lifestyle_demo` (or pull the committed db + originals).

## Phase 3 (part) — article post-type template variants — 2026-07-11 ✅

Built the **post-type → template variant** portion of Phase 3 at the owner's
request (article templates matching the iNews single-post pages). The rest of
Phase 3 (full StreamField block set) is still pending.

**Built**
- Article templates rebuilt to the iNews `.main-content` / `.single-post`
  structure (`article_base.html` two-column + `article_page.html` with lead media,
  title, meta/byline, body, share box, shoppable "From the Shop", author box,
  related reading).
- **Lead media per post type**, matching the iNews templates:
  - `standard` (+ feature/interview/review/guide/event/list) → hero image
  - `video` → `.inews-post-video` iframe (from new `lead_video_url`)
  - `audio` → `.inews-post-audio` iframe (from new `lead_audio_url`)
  - `gallery` → `.gallery-slider` owl carousel (from new `ArticleGalleryImage`
    inline; owl init added)
  - `quote` → `.single-post.quote`, headline leads as `<q>` then image
- Added **`quote`** and **`audio`** to `POST_TYPE_CHOICES`; new fields
  `lead_video_url`, `lead_audio_url`, and the `ArticleGalleryImage` orderable
  (migration `0004`). Phase 3 CSS appended.
- Seed extended: video / audio / quote demo articles + gallery images (15 total).

**Files touched**
- `apps/lifestyle/models.py`, `migrations/0004_*.py`,
  `templates/lifestyle/{article_base,article_page}.html`,
  `static/lifestyle/pp-lifestyle.css`, `management/commands/load_lifestyle_demo.py`,
  `db.sqlite3` + `media/original_images/`

**Verify (all pass)** — each variant renders its iNews layout: standard
(thumb/content/share), video (iframe), gallery (owl carousel + 4 slides + nav),
quote (`<q>` title, quote class), audio (iframe). Screenshot confirmed the
gallery single-post matches iNews. `check` clean.

---

## Phase 3 (complete) — StreamField block set — 2026-07-11 ✅

**Built** (`apps/lifestyle/blocks.py` + `templates/lifestyle/blocks/*`)
- `ArticleBodyBlock` with: **rich paragraph** (curated features), **pull quote**,
  **full-bleed image** (alt required), **image gallery**, **video** (Wagtail
  `EmbedBlock`/oEmbed), **product card** (Oscar product → image/name/"View at
  Pier & Paddock", never price-led), **FAQ** (Q/A `<details>`), **key takeaways**,
  **table** (HTML), **divider**, **inline ad** (drops an `AdZone` in-content).
- `ArticlePage.body` now uses the full block set (migration `0005`); block CSS
  appended to `pp-lifestyle.css`; seed enriched so every article body exercises
  key-takeaways / pull-quote / product-card / FAQ / divider / inline-ad.

**Verify:** all blocks render in a seeded article (key takeaways, pull quote,
product card with "View at Pier & Paddock" CTA, FAQ, divider, inline ad placeholder).
`check` clean.

**Deviations:** `table` uses a RawHTMLBlock (not `wagtail.contrib.table_block`) to
avoid another app; the in-body `product` block uses an IntegerBlock product-id (no
generic Oscar model chooser out of the box). FAQPage/schema emission for the FAQ
block lands in Phase 6.

## Phase 4 — article rail: Latest News + Sponsored Products — 2026-07-11 ✅

**Built**
- **`SponsoredProductSlot`** snippet (product, hook, advertiser, order, active) —
  the Revive product-listing seam.
- `{% latest_news %}` tag → the iNews sidebar widget markup fed the 5 most recent
  articles (current excluded).
- `{% sponsored_products %}` tag → **duplicates the Latest News widget**, retitled
  "Sponsored Products" with a small-caps gold-ruled "Sponsored" label. Resolution:
  curated slots → the article's `related_products` → same-category/recent fallback.
  Every link carries `rel="sponsored"` + `?ppl_src=sponsored&ppl_article=<slug>`
  tracking. The tag docstring documents the future Revive contract (zone ID in,
  `[{image,title,url,advertiser}]` out).
- Wired both into `article_base.html`'s sidebar (below the sidebar ad). Sidebar CSS
  added. Seed creates 4 curated slots.

**Files touched**
- `apps/lifestyle/models.py`, `migrations/0006_*.py`,
  `templatetags/lifestyle_tags.py`,
  `templates/lifestyle/includes/{_latest_news,_sponsored_products}.html`,
  `templates/lifestyle/article_base.html`, `static/lifestyle/pp-lifestyle.css`,
  `management/commands/load_lifestyle_demo.py`, `db.sqlite3` (slots)

**Verify (all pass):** article rail shows Latest News then Sponsored Products;
sponsored links carry `rel="sponsored"` + tracking; Latest News excludes the
current article. `check` clean.

## Phase 5 — /advertise/ + subscriptions + Members hook — 2026-07-11 ✅

**Built**
- **`/advertise/`** (real form, replacing the Phase-1 stub): positioning + audience
  bullets + form (name, company, email, phone, budget, message). On submit: emails
  `advertise@pierandpaddock.com` (console backend in dev), stores an
  **`AdvertiseInquiry`**, shows confirmation. **Honeypot** (`website` field) +
  per-IP rate limit (5/hour via cache).
- **Subscriptions** — one endpoint `/lifestyle/subscribe/` for every form. New
  **`MailchimpClient`** wrapper (INACTIVE): reads keys from settings; while disabled
  the endpoint saves a **`PendingSubscriber`** (email, source, consent) and returns
  success. **`manage.py sync_pending_subscribers`** pushes them once keys exist.
- **Crest tie-in:** subscribing = eligibility for Member. If the email matches a
  store account, `services.set_marketing_opt_in` → 1 crest; otherwise the
  PendingSubscriber records the intent. Members copy throughout ("Join P&P
  Members…", never "newsletter"), double-opt-in language + Privacy Policy link.
- Subscribe surfaces: **article sidebar** widget, an **inline** end-of-article unit,
  and a **footer strip** on the magazine (`base.html`) — plus a `?subscribed=`
  confirmation banner. `AdvertiseInquiry` + `PendingSubscriber` are Wagtail snippets
  (reviewable in `/cms-admin/`).

**Files touched**
- `apps/lifestyle/{models,forms,integrations,views}.py`,
  `migrations/0007_*.py`, `management/commands/sync_pending_subscribers.py`,
  `templates/lifestyle/{advertise,base,article_base,article_page}.html` +
  `includes/_subscribe.html`, `static/lifestyle/pp-lifestyle.css`, `config/urls.py`

**Verify (all pass):** advertise POST persists + emails + confirms; honeypot blocks
spam; subscribe stores PendingSubscriber (source/consent) with Mailchimp disabled;
existing-account subscribe → 1 crest; 3 subscribe surfaces render; sync command
reports pending while disabled. `check` clean.

**Owner placeholder:** set `MAILCHIMP_API_KEY` / `MAILCHIMP_LIST_ID` +
`LOYALTY_MARKETING_ENABLED=True`, then run `sync_pending_subscribers`.

---

## Ad-hoc / early items

- **2026-07-11 — Storefront primary nav "Blog" → "Lifestyle"** (a Phase 7 item,
  done early at the owner's request). Both the desktop and mobile menus in
  `templates/oscar/partials/_header.html` now link to `/lifestyle/`.
- **2026-07-11 — Shared footer restructure** (`_footer.html`, affects both
  properties): new **Lifestyle** column (Latest Stories + the six magazine
  categories, data-driven via `{% lifestyle_nav %}`); moved **Terms & Conditions,
  Privacy, Advertise** into **Customer Care**; removed the **Journal** link and the
  redundant bottom legal row. Now a 5-column footer.

---

## Owner (Mike) — outstanding placeholders

| Placeholder | Status | Notes |
|---|---|---|
| iNews `TEMPLATE_DIR` | ✅ present | `/Users/querybridge/envs/idcwatch/inews_396ccbc46b5d2d6840665ca80b82bc68` — Phase 1 unblocked |
| `MAILCHIMP_API_KEY` / `MAILCHIMP_LIST_ID` | ⏳ pending | settings constants, empty; subs stored locally (Phase 5) |
| Revive Adserver endpoint | ⏳ pending | `REVIVE_ENABLED=False`; local placeholder creatives (Phase 1/4) |
| GA4 / Search Console IDs | ⏳ pending | `GA4_MEASUREMENT_ID` empty (Phase 6) |
