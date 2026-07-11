# LIFESTYLE_MAGAZINE.md — Pier & Paddock Lifestyle (Wagtail Content Hub)

## Purpose

Add an online lifestyle magazine — **Pier & Paddock Lifestyle** — to the existing Pier & Paddock store (Django Oscar + zwat, see `CLAUDE.md`). The magazine is a top-of-funnel acquisition engine: draw the affluent F1 / sailing / luxury-auto / watch-collector audience in via SEO, social, and organic AI discovery, then route them to the shop. Monetization: banner ads + product listing ads (placeholder now, Revive Adserver later). Subscribers become **Crest Members** (tier 1, see `LOYALTY_PROGRAM.md`).

**Tone/brand guardrails:** never price-forward, never discount-y, never gauche. Editorial voice is a knowledgeable insider — the harbor and the grid. Palette: navy `#1B2A41`, gold `#9A7B43`, warm off-white `#F6F3EE`. Serif display: GFS Baskerville (or template equivalent); sans: Carlito/Calibri fallback stack.

---

## How Claude Code must work through this document

This spec is split into **phases**. Each phase is independently buildable, verifiable, and committable. To avoid context loss:

1. **Work one phase at a time.** Do not start a phase until the previous phase's checklist passes.
2. **Maintain `LIFESTYLE_PROGRESS.md`** at the repo root. After each phase: append the phase number, date, what was built, file paths touched, any deviations from this spec, and any placeholders left for the owner (Mike). Read this file at the start of every session before doing anything else.
3. **Commit per phase** with message `lifestyle: phase N — <summary>`.
4. **Never modify the zwat storefront templates** except where a phase explicitly says so (homepage link, footer include).
5. If something in this spec conflicts with the actual codebase, prefer the codebase's existing conventions and record the deviation in `LIFESTYLE_PROGRESS.md`.

### Placeholders the owner must supply (do not block on these — stub and log them)

| Placeholder | Where used | Stub behavior |
|---|---|---|
| `TEMPLATE_DIR` | Local path to the extracted **INews** template package (TemplateMonster ID 110671 — "INews Responsive Newspaper HTML Website Template", demo: https://demo.templatemonster.com/demo/110671.html - /Users/querybridge/envs/idcwatch/inews_396ccbc46b5d2d6840665ca80b82bc68). Static HTML5/Bootstrap template with multiple predefined homepages (use **Home 3**) and multiple post styles. Look for it in the repo (e.g. `inews/`, `template/`, or `vendor/inews/`); if not present, halt Phase 1 and ask Mike for the path to the purchased/extracted package. | Halt Phase 1 and request path |
| `MAILCHIMP_API_KEY`, `MAILCHIMP_LIST_ID` | Subscription form | Store submissions locally in a `PendingSubscriber` model; sync command for later |
| Revive Adserver endpoint | Ad zones, sponsored products | Serve local placeholder creatives |
| GA4 / Search Console IDs | Analytics, sitemaps | Settings constants, empty by default |

---

## PHASE 0 — Wagtail installation & wiring (no visuals)

**Goal:** Wagtail runs inside the existing Django/Oscar project without breaking the store.

- Install `wagtail` (latest stable compatible with the project's Django version). Add required apps (`wagtail`, `wagtail.admin`, `wagtail.images`, `wagtail.documents`, `wagtail.snippets`, `wagtail.sites`, `wagtail.users`, `wagtail.contrib.settings`, `wagtail.contrib.routable_page`, `wagtail.sitemaps`, `taggit`, `modelcluster`).
- URL wiring, in this order of precedence in the root `urls.py`:
  - `path('cms-admin/', include(wagtailadmin_urls))` — **do not** use `/admin/`; Django admin and Oscar dashboard keep their existing URLs.
  - `path('documents/', include(wagtaildocs_urls))`
  - `path('lifestyle/', include(wagtail_urls))` — **all Wagtail pages live under `/lifestyle/`**. There is no `/blog/`. Add a permanent redirect `path('blog/<path:rest>', ...)` → `/lifestyle/<rest>` and `/blog/` → `/lifestyle/` (301) so any early links or habits resolve correctly.
- Create app `lifestyle/` for all page models, blocks, template tags, and views described below.
- Media/image settings: ensure `WAGTAILIMAGES_*` renditions work with the project's storage; enable WebP output (`WAGTAILIMAGES_FORMAT_CONVERSIONS = {'jpeg': 'webp', 'png': 'webp'}` where supported).
- Create the Wagtail Site root: a `LifestyleIndexPage` (defined in Phase 2) mounted so its URL is `/lifestyle/`.

**Verify:** store pages unaffected; `/cms-admin/` loads; `/lifestyle/` returns a stub page; `/blog/` 301s to `/lifestyle/`.

---

## PHASE 1 — iNews template intake & static assets

**Goal:** the iNews template's assets are integrated as the magazine skin, rebranded.

- The template is **INews** (TemplateMonster ID 110671 found here: /Users/querybridge/envs/idcwatch/inews_396ccbc46b5d2d6840665ca80b82bc68), a static HTML5/Bootstrap newspaper/magazine template. The live demo at https://demo.templatemonster.com/demo/110671.html is the visual ground truth for layout decisions — when in doubt about how a section should look or behave, match the demo.
- Copy CSS/JS/fonts/images from `TEMPLATE_DIR` into `lifestyle/static/lifestyle/`. Namespace everything under `/static/lifestyle/` so it cannot collide with zwat assets.
- Identify these template pages and stage them as Django template bases in `lifestyle/templates/lifestyle/`:
  - **Home Page 3** → `index.html` base for the magazine landing page (this is the layout the P&P storefront homepage will link to).
  - Article/single-post page → `article_base.html`
  - Category/archive page → `category_base.html`
  - Any author/search/404 pages the template ships with.
- **Rebrand:** replace every instance of the INEWS logo (image and text-mark) with **"Pier & Paddock Lifestyle"**. Prefer a text-mark in the serif display face (navy on off-white; gold accent rule beneath) rendered as SVG so it stays crisp; keep the template's logo dimensions so the layout doesn't shift. Also update `<title>` suffixes, favicon references, and any "iNews" strings in footer credits.
- **Ad banners:** keep every ad slot the template defines (leaderboard, in-content, sidebar, footer — inventory them all and list them in `LIFESTYLE_PROGRESS.md` with their pixel dimensions). For each slot, generate a placeholder creative: solid `#666666` PNG at the slot's exact dimensions with centered white text **"Your Ad Here"**. Every placeholder links to `/advertise/`.
  - Implement ad slots as a template tag `{% ad_zone "leaderboard_top" %}` backed by an `AdZone` snippet (name, dimensions, active creative, target URL). This is the seam where **Revive Adserver** zone tags will drop in later — the template tag should render either the local placeholder or, when `REVIVE_ENABLED=True`, a Revive invocation tag stored on the zone. Build the abstraction now, integrate Revive later.
- **Primary nav:** replace the template's nav with exactly: **Fashion, Motorsports, Watersports, Business, Entertainment, Health, Shop**. The first six link to their category pages (Phase 2); **Shop** links to the storefront root (`/`). Nav is data-driven from the category pages, not hardcoded, with Shop appended.
- **Footer:** keep the template's magazine footer, then render the **current P&P storefront footer directly below it** by including the existing zwat footer partial (extract it into a shared include if it isn't one already, so both properties render the same footer from one source).

**Verify:** magazine base templates render standalone with correct branding, nav, placeholder ads, and stacked footers; zero console 404s on assets.

---

## PHASE 2 — Page models & information architecture

**Goal:** the Wagtail content model. No fancy editor UI yet — structure first.

```
LifestyleIndexPage  (/lifestyle/)            — Home Page 3 layout
 └── CategoryPage ×6 (/lifestyle/fashion/ …) — Fashion, Motorsports, Watersports,
                                               Business, Entertainment, Health
      └── ArticlePage (/lifestyle/<category>/<slug>/)
AuthorIndexPage (/lifestyle/authors/)
 └── AuthorPage  (/lifestyle/authors/<slug>/)
AdvertisePage   (/advertise/ — plain Django view is fine, see Phase 5)
```

- **ArticlePage** fields:
  - `post_type` — **a required choice field the author picks in the editor** (see Phase 3 for the list). Drive template variations and schema.org type from it.
  - `subtitle` (dek), `hero_image` + required `hero_alt_text` + optional caption/credit, `authors` (M2M to AuthorPage), `publish_display_date`, `updated_date`, `reading_time` (auto-computed), `tags` (taggit), `is_sponsored` (bool — forces a visible "Partner Content" disclosure band and `rel="sponsored"` on outbound links), `related_products` (up to 4 Oscar products, for shoppable cards), `related_articles` (auto by tag/category with manual override).
  - `body` — StreamField (Phase 3).
  - SEO panel: `seo_title`, `search_description`, `canonical_url` override, `og_image` override, `noindex` toggle.
- **CategoryPage**: intro (rich text, 150–300 words of editorial positioning — this is the topical-authority hub copy), hero, featured articles (manual curation slots), then reverse-chron listing with pagination. Category color accent optional.
- **AuthorPage**: portrait, bio, credentials/title, social links, article listing. This exists for E-E-A-T — real bylines with real bios.
- **LifestyleIndexPage** maps content into the Home Page 3 layout: hero/featured slot(s), per-category rails, latest grid, trending (by recent view count if cheap, else most-recent fallback), ad zones where the template places them.
- Seed content: create the six categories, 3 demo authors, and ~12 demo articles across categories/post types so every template state is demonstrable.

**Verify:** full tree navigable; URLs exactly `/lifestyle/<category>/<slug>/`; pagination, category hubs, author pages render.

---

## PHASE 3 — Article editor: post types & StreamField body

**Goal:** an author-friendly editor where the writer picks the post type at creation.

- `post_type` choices (choice field, shown at the top of the Content panel):
  - `standard` — Standard Article
  - `feature` — Long-form Feature
  - `gallery` — Photo Gallery
  - `video` — Video Feature
  - `interview` — Interview / Profile
  - `review` — Review (gear, watches, experiences)
  - `guide` — Guide / How-To (evergreen, e.g. "A collector's guide to regatta season")
  - `event` — Event Coverage (F1 rounds, regattas, Cars & Coffee, auctions)
  - `list` — Curated List ("Ten watches that belong on a bridge deck")
- Post type drives: article template variant (gallery gets a lightbox grid, video gets a lead player, review gets a verdict block, event gets date/venue metadata), the schema.org `@type` (Phase 6), and a badge on cards/listings.
- **StreamField blocks** (`body`): rich paragraph, pull quote, full-bleed image (alt required), image gallery, embedded video (YouTube/Vimeo via oEmbed), **product card block** (select an Oscar product → renders image, name, "View at Pier & Paddock" — never a price-led CTA), FAQ block (Q/A pairs — also emits FAQPage schema), key-takeaways block, table, divider, inline ad slot block (drops an `AdZone` in-content).
- Editor QoL: preview works for all post types; required alt text enforced; word count / reading time shown.

**Verify:** create one article of each post type in `/cms-admin/`; each renders with its variant template and badge.

---

## PHASE 4 — Article sidebar: Latest News + Sponsored Products

**Goal:** the left rail of the article template.

- Keep the template's **Latest News** section (feed it the 5 most recent published `ArticlePage`s, excluding the current one).
- **Duplicate that section's markup/styling directly below it, retitled "Sponsored Products."** It renders 3–5 product units: image, product name, one-line hook, link. Visually consistent with Latest News but clearly labeled "Sponsored" (small caps label, gold rule) and each link carries `rel="sponsored"` + click-through tracking parameters.
- Architecture mirrors the ad zones: a `SponsoredProductSlot` model/snippet now (manually curated from Oscar products, or auto-filled from `related_products` / same-category bestsellers as fallback), behind a template tag `{% sponsored_products %}`. When Revive integration lands, this tag becomes the seam for the customized Revive product-listing zone (Google-Shopping-style units served by Revive). Document the intended Revive contract in code comments: zone ID in, JSON of {image, title, url, advertiser} out.

**Verify:** article pages show Latest News then Sponsored Products in the left rail; sponsored links carry `rel="sponsored"`.

---

## PHASE 5 — /advertise/ + subscriptions (Mailchimp-pending) + Members hook

**Goal:** the two conversion surfaces that aren't the shop.

- **/advertise/**: a simple, on-brand page (magazine skin) — one short positioning paragraph ("Reach the collector at the harbor and the grid"), audience bullets, and a form: name, company, email, phone (optional), budget range (optional dropdown, tasteful), message. On submit: send email to `advertise@pierandpaddock.com` (Django email backend; console backend in dev), store an `AdvertiseInquiry` row, show a confirmation. Honeypot + basic rate limiting; no CAPTCHA branding clutter.
- **Subscriptions**: the template's newsletter forms (footer, sidebar, and an inline end-of-article unit) all post to one endpoint.
  - Since the Mailchimp account is pending: write a `MailchimpClient` wrapper reading `MAILCHIMP_API_KEY`/`MAILCHIMP_LIST_ID` from settings. If unset, save to `PendingSubscriber` (email, source page, timestamp, consent bool) and return success. Provide `manage.py sync_pending_subscribers` to push to Mailchimp once keys exist.
  - **Crest tie-in:** subscribing = eligibility for **Member** (1 crest). If the email matches an existing store account, flag membership per `LOYALTY_PROGRAM.md`; otherwise store the intent so account creation links it. Copy on the form should sell the benefit: "Join P&P Members — early access, the market brief, and the Vault." Never "sign up for our newsletter."
- Double-opt-in consent language + link to privacy policy on every form.

**Verify:** advertise form emails + persists; subscribe stores `PendingSubscriber` with no API key set; sources tracked.

---

## PHASE 6 — SEO, feeds & AI discovery layer

**Goal:** everything crawlers and LLMs need. This phase is pure head/markup/infrastructure — no visual changes.

- **Structured data (JSON-LD)** on every page:
  - `Article`/`NewsArticle`/`Review`/`FAQPage`/`VideoObject`/`ItemList` chosen by `post_type`; include headline, dates, author (linked `Person` with `sameAs` socials), publisher `Organization` (P&P logo), image, wordCount.
  - `BreadcrumbList` on all pages; `Organization` + `WebSite` (with `SearchAction`) on the index; `Product` schema on product card blocks (name, image, brand, url — omit price, consistent with brand rules).
- **Meta layer:** unique titles (`<seo_title or title> | Pier & Paddock Lifestyle`), meta descriptions, canonical tags (respect the override field), OpenGraph + Twitter Card (large image) with per-page og:image fallback chain (og override → hero → site default 1200×630).
- **Sitemaps:** `wagtail.contrib.sitemaps` at `/sitemap.xml` including lifestyle pages; ensure the store's sitemap and this one are both referenced in `robots.txt` (sitemap index if needed).
- **Feeds:** RSS/Atom at `/lifestyle/feed/` plus per-category feeds `/lifestyle/<category>/feed/` (full metadata, hero image enclosure). Feeds matter for both syndication and AI crawlers.
- **AI discovery:**
  - `llms.txt` at site root: brand summary, what the magazine covers, category URLs, feed URLs, contact.
  - Clean semantic HTML (`<article>`, `<time datetime>`, single `<h1>`, hierarchical headings) — audit the iNews markup and fix violations.
  - FAQ + key-takeaways blocks (Phase 3) exist partly for answer-engine extraction; encourage their use in editorial guidelines.
  - `robots.txt`: allow GPTBot/ClaudeBot/PerplexityBot etc. explicitly (this is a discovery play, not a paywall), disallow `/cms-admin/`.
  - IndexNow ping on publish (Bing/others); optional simple ping to Google sitemap endpoint.
- **Performance (Core Web Vitals):** responsive renditions with `srcset`/`sizes`, WebP, lazy-load below-the-fold images (hero eager + `fetchpriority=high`), width/height attributes everywhere (no CLS — especially the ad slots: reserve their exact dimensions), defer non-critical JS from the template, cache page output (template fragment or per-page cache), compress static assets.
- **Internal linking:** related-articles unit (3 per article), category hub links in article header breadcrumb, automatic in-article product cards linking to shop, and a "From the Shop" unit on category pages. Every article should link to ≥1 shop page and ≥2 other articles.
- **Analytics & consent:** GA4 snippet behind a settings flag; outbound shop clicks and sponsored clicks fire events (`lifestyle_to_shop`, `sponsored_click`, `subscribe_submit`); lightweight consent banner if required.

**Verify:** Rich Results Test passes for one article of each schema type; Lighthouse ≥ 90 performance/SEO on article + index (throttled); feeds validate; `/sitemap.xml`, `/robots.txt`, `/llms.txt` correct.

---

## PHASE 7 — Storefront integration & polish

**Goal:** stitch the two properties together.

- **Storefront homepage → magazine:** on the zwat **Home Page 3** storefront homepage, the designated link/section points to `/lifestyle/`. Add a "From the Lifestyle Journal" strip on the storefront homepage: 3 latest articles (image, category badge, title) — one template include reading published `ArticlePage`s.
- Magazine nav "Shop" → storefront; storefront nav gains "Lifestyle."
- Shared footer confirmed identical on both properties (single include).
- 404 page for `/lifestyle/*` in the magazine skin with latest articles + search.
- Search within the magazine (Wagtail search backend, template's search UI).
- Final QA checklist: all placeholder ads sized/linked, all seed articles have alt text, mobile pass on index/category/article/advertise, redirects (`/blog/*`) verified, `LIFESTYLE_PROGRESS.md` finalized with the owner's outstanding placeholders (template path if unresolved, Mailchimp keys, Revive endpoint, GA4 ID).

---

## FUTURE PHASES (do not build now — leave seams)

- **Revive Adserver:** swap `AdZone` and `SponsoredProductSlot` internals for Revive invocation tags; customize Revive for product-listing units (image/title/url payloads). The template tags are the only touch points.
- **Mailchimp live:** set keys, run `sync_pending_subscribers`, wire double opt-in webhooks, tag subscribers by source category for segmented sends.
- **Membership deep-link:** subscriber → account creation → Crest Member provisioning automated.
- **Editorial workflow:** Wagtail moderation/workflow states, scheduled publishing calendars, contributor roles.
- **Programmatic distribution:** Apple News / Flipboard feeds, Pinterest rich pins (article schema already supports), web stories for event coverage.
