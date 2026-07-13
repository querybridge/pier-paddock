# Pier & Paddock — Luxury Watch Demo Store

A polished **demo ecommerce store** for high-end watches — built with
**Django + django-oscar** (zwat theme) and paired with an editorially independent
**Wagtail lifestyle magazine** at `/lifestyle/` (iNews theme).

> **This is a sales/UX demo, not a production site.** Shoppers can browse, filter,
> search, view rich product detail, manage a cart and wishlist/vault, register and
> sign in, and walk the entire checkout — but **purchasing is intentionally disabled
> at the final step**. No order is ever created and no payment is ever taken.

`Pier & Paddock` is a **placeholder brand name**. It's defined once in
`config/settings.py` (`BRAND_NAME`) and surfaced everywhere through a context
processor, so the whole storefront re-brands by changing a single value — no
template edits.

---

## What it demonstrates

A complete, believable luxury-watch storefront:

- **Catalogue** of ~50 fictional watches across Rolex, Audemars Piguet, Patek
  Philippe, Omega, Cartier, Vacheron Constantin, Richard Mille, IWC and
  Jaeger-LeCoultre, with realistic specs, reference numbers and market-style
  prices. (Imagery is generated/placeholder or licensed sample photography —
  no scraped brand photos.)
- **Home page** — animated hero carousel (auto-rotating, 5s per slide), featured
  collections, a new-arrivals slider with hover "rollover" cards, a trust strip
  and a **"From the Lifestyle Journal"** strip of the latest magazine stories.
- **Shop / product listing** — faceted sidebar (brand, collection, price, case
  material, condition), sorting and pagination; cards with image rollover,
  quick add-to-cart and save-to-vault.
- **Search** — keyword search across brand, model and reference.
- **Product detail** — image gallery, full specification table, condition &
  box-and-papers badges, customer reviews on flagship pieces, related products,
  add-to-cart, **Save to Vault** and **Compare**.
- **Compare** — pick up to 3 watches and compare their specs side by side.
- **The Crest Membership** — the signature loyalty program. Membership is shown
  as **1–5 crests** driven by *lifetime spend*: Member → Patron → Collector →
  Curator → Steward. A member dashboard shows the crest mark, progress to the
  next tier, unlocked benefits (with locked teasers above), **Retailer's Credit**,
  a tier-scaling concierge and the quarterly market report. Tier thresholds are
  configurable. Because checkout is disabled, an **Operator Console** (`/console/`,
  staff-only) drives tier progression live — its **Simulate purchase** control
  advances a member on the spot — and surfaces program analytics (tier mix,
  credit liability, grail-demand). See **The Crest Membership** section below.
- **The Vault** — an account-only **investment view** of a collector's watches:
  pieces you *own* show purchase price, latest market value and the change vs.
  what you paid; pieces you're *watching* show the current market value, with a
  portfolio summary on top. **Price tracking (live values, portfolio total,
  sparklines) is a Collector-tier benefit**, and Curator+ members see **first-look**
  pieces here before public listing. (Market values are dummy data, structured to
  later source real pricing from an external watch-pricing API.)
- **Merchant Portal** — a branded, supplier-scoped back office (`/merchant/`, staff)
  where a listing partner (a stand-in for the IDC-style dropship supplier) **adds
  listings manually**, **configures their XML product feed** (a configurable but
  inactive integration — set the URL, toggle it, run a simulated "Sync now"), and
  **monitors their sales** (units/revenue, top sellers, per-piece). Sales derive
  from the same simulated-purchase activity as the loyalty program, so an Operator
  Console "Simulate purchase" moves a merchant's numbers live.
- **Cart & checkout** — fully navigable multi-step checkout (shipping address →
  shipping method → payment → preview) with the **payment step disabled** and a
  clear "payments are disabled in this demo" notice. Two named shipping methods
  (complimentary insured overnight, or paid Saturday delivery).
- **Accounts** — registration, login, profile, order history and address book.
- **Lifestyle magazine** — an editorially independent **Wagtail 7 content hub** at
  `/lifestyle/` ("Pier & Paddock Lifestyle"), skinned with the "iNews" theme. Category
  hubs, multi-format articles (standard, feature, gallery, video, audio, review, guide,
  interview, list, quote), author pages, and a **StreamField** body (rich text,
  pull-quotes, full-bleed images, galleries, shoppable product cards, FAQs,
  key-takeaways, embeds, inline ads). Each article has a Latest-News + **Sponsored
  Products** rail, an `/advertise/` enquiry funnel and a **Members** newsletter sign-up
  (Mailchimp-pending; ties into the Crest program). Full **SEO / AI-discovery** layer —
  JSON-LD by post type, OpenGraph/Twitter, `/sitemap.xml`, RSS/Atom feeds, `robots.txt`,
  `llms.txt` — plus a magazine-skinned search and 404. Edited in the **Wagtail CMS admin**
  (`/cms-admin/`). Ad slots (`AdZone`) and sponsored products are wired as **Revive
  Adserver** seams (inactive placeholders for now).
- **Content** — About, FAQ and Contact pages (contact posts to the console email
  backend) and a custom 404. (The old blog/journal is superseded by the Lifestyle
  magazine above — `/blog/*` now 301-redirects to `/lifestyle/*`.)

---

## Tech stack

| Concern   | Choice |
|-----------|--------|
| Framework | Django 5.2 + django-oscar 4.1 |
| CMS / magazine | **Wagtail 7.4** — the Lifestyle content hub at `/lifestyle/`, edited in the Wagtail CMS admin at `/cms-admin/` |
| Database  | SQLite (`db.sqlite3`) |
| Images    | Pillow — generated placeholder imagery; sorl-thumbnail (store) + Wagtail renditions → WebP (magazine) |
| Search    | Haystack simple backend (store); substring search over live articles (magazine); faceted shop filtering via a custom ORM view |
| Custom apps | `loyalty` (Crest membership + Operator Console), `merchant` (Merchant Portal), `vault` (investment tracking), `compare`, `shop` (faceted browse), **`lifestyle`** (Wagtail magazine), `blog`, `pages`, plus forked `checkout` (payments disabled) and `shipping` (named methods) |
| Email (built, inactive) | **SendGrid** for transactional mail, **Mailchimp** for marketing — wired in `apps/loyalty/emails.py` but disabled in the demo (no keys, no network calls) |

---

## Running it

Requires **Python 3.10+**. A virtualenv lives in this directory (`bin/`, `lib/`,
`pyvenv.cfg`) but is **not** committed — recreate it, then install dependencies:

```bash
python3 -m venv .                  # (re)create the venv in this directory
./bin/pip install -r requirements.txt
```

The repository ships with a populated **`db.sqlite3`** and product imagery, so
you can run the demo immediately:

```bash
./bin/python manage.py migrate     # no-op if already migrated; safe to run
./bin/python manage.py runserver
```

Then open **http://127.0.0.1:8000/**.

### Rebuild the demo data from scratch (optional)

To regenerate the catalogue, imagery, accounts and vault data deterministically:

```bash
./bin/python manage.py load_demo_catalogue
```

This clears and rebuilds everything (it's idempotent and reproducible).

### Seed the Crest membership demo

After the catalogue is loaded, seed the membership program — one logged-in-ready
member per tier, plus valuation history, a sample market report, first-look flags
and seeded credit/grail/notifications:

```bash
./bin/python manage.py load_loyalty_demo
```

This is idempotent (re-running resets the per-tier members). Run it after
`load_demo_catalogue` if you rebuild from scratch.

### Seed the Lifestyle magazine (optional)

The magazine ships in `db.sqlite3` too. To rebuild it from scratch, run in order:

```bash
./bin/python manage.py lifestyle_bootstrap   # Wagtail site + landing/category/author pages
./bin/python manage.py lifestyle_ads         # ad zones (Revive-ready placeholders)
./bin/python manage.py load_lifestyle_demo   # authors, articles, StreamField bodies, imagery
```

Content is authored in the **Wagtail CMS admin** at `/cms-admin/` (sign in as the
superuser — see below). Magazine images are committed as Wagtail renditions alongside
their DB rows, so the demo renders on deploy without regenerating; after editing content,
re-render the `/lifestyle/*` pages and recommit `media/images/` + `db.sqlite3` together.
Newsletter sign-ups queue locally (`PendingSubscriber`) until Mailchimp keys exist —
`./bin/python manage.py sync_pending_subscribers` flushes them when configured.

---

## The Crest Membership

Membership status is **1–5 crests**, driven by **lifetime spend** (a single
high-value purchase can jump several crests at once):

| Crests | Tier | Earned by | Headline unlocks |
|--------|------|-----------|------------------|
| 1 | **Member**    | Account + marketing opt-in | Unlimited Vault, market newsletter |
| 2 | **Patron**    | First purchase | 24-hr early access, alerts, email concierge, quarterly report |
| 3 | **Collector** | ≥ $25,000 lifetime | **Vault price tracking**, **Retailer's Credit**, grail list |
| 4 | **Curator**   | ≥ $75,000 lifetime | 72-hr first-look, reserve/hold, priority sourcing |
| 5 | **Steward**   | ≥ $200,000 lifetime **or** invitation | Personal concierge, top trade-in terms, marquee invitations |

Thresholds and the credit accrual rate are editable in the Operator Console
(`/console/config/`). The crest rule lives in one place
(`Membership.recompute()`), so every path — console controls, the demo checkout,
and the seed command — advances members identically.

**Customer surfaces** (zwat-skinned, under `/account/`): the membership dashboard
(`/account/membership/`), the unified Vault (`/account/vault/`), the grail list
(`/account/grail/` — a matched piece surfaces a **"View now"** pill straight to
the shop), the alerts/notification feed (`/account/alerts/`), and the public
marketing page at `/membership/`.

The **crest mark** is a minimal monogram shield (black shield, muted-gold "P&P"
monogram and rule), rendered 1–5 times to show the level — filled = earned,
outline = locked. It's a reusable SVG component in three sizes plus a multi-size
`.ico` favicon (`static/img/crest.ico`, regenerated by `apps/loyalty/crest_icon.py`).

**Operator Console** (`/console/`, staff-only — a branded-clean back-office UI):
analytics (tier mix, **Retailer's Credit liability**, grail demand), a member list
+ detail with clearly-labelled **demo controls** (Simulate purchase, set spend,
grant credit, issue invitation, mark grail matched), inventory early-access
flagging, and program configuration.

> **Demo flow:** log in as each tier to show the member experience, then sign in
> as the **operator** (`retailer@pierpaddock.demo`) and open the Operator Console,
> pick the **Patron**, hit **Simulate purchase** on a ~$20K watch, and watch them
> advance to **Collector** live with credit accrued — then open the **Merchant
> Portal** (`merchant@meridianwatch.demo`) to see that same sale on the supplier's
> sales monitor.

---

## The Merchant Portal

A second back office (`/merchant/`, staff), styled in the same branded-clean family
as the Operator Console but for the **supply side** — the merchant who lists
watches on Pier & Paddock. It's scoped to a single Oscar `Partner`, so each
merchant sees only their own inventory and sales.

- **Dashboard** — sold-this-month, revenue, lifetime totals, top sellers, feed status.
- **Listings** — every watch they supply, with units sold; **Add a listing** form
  creates a real (browsable) product + stockrecord under their partner.
- **XML Feed** — feed URL, enable/auto-sync toggles, last-synced status and a
  **Sync now** button. Inactive in the demo (no external fetch) — mirrors the
  SendGrid/Mailchimp pattern; production would parse the feed and upsert listings.
- **Sales** — per-piece and recent-sales monitor.

Sales are derived from the loyalty `DemoPurchase` log scoped to the merchant's
products (checkout is disabled, so that's the stand-in for orders) — which is why
an Operator Console **Simulate purchase** on one of their pieces updates the
merchant's numbers live. Roles are kept separate: the loyalty operator can't open
the portal and the merchant can't open the loyalty console (a superuser sees both).

> The underlying `Partner` is the catalogue's existing supplier; the portal shows
> a **generic display name** so the IDC name stays out of the UI (footer only).

---

## Demo accounts

| Role                   | Email                       | Password      | Surface / use for |
|------------------------|-----------------------------|---------------|-------------------|
| Customer               | `demo@example.com`          | `Demo1234!`   | the shopper experience (vault, orders, addresses) |
| Operator (loyalty ops) | `retailer@pierpaddock.demo` | `Retail1234!` | **Operator Console** (`/console/`) — runs the Crest program. Staff, *not* superuser |
| Merchant               | `merchant@meridianwatch.demo`| `Merchant1234!`| **Merchant Portal** (`/merchant/`) — a supplier listing inventory & watching their sales (a generic stand-in for the IDC-style dropship supplier). Staff, *not* superuser |
| Magazine editor        | `editor@pierpaddock.demo`   | `Editor1234!` | **Wagtail CMS admin** (`/cms-admin/`) — authors & publishes the Lifestyle magazine. In the Wagtail **Editors + Moderators** groups; *not* staff/superuser, so it can't reach `/admin/`, the Operator Console or the Merchant Portal |
| Admin (superuser)      | `admin@example.com`         | `Admin1234!`  | everything: Django admin (`/admin/`), Oscar dashboard (`/dashboard/`), **Wagtail CMS admin (`/cms-admin/`)**, console **and** portal |

**Crest membership — one member per tier** (shared password `Crest1234!`), each
seeded so the screen is fully populated for a walkthrough:

| Tier | Email | Lifetime spend | What it shows |
|------|-------|---------------:|---------------|
| Member    | `member@pierpaddock.demo`    | $0       | Crest 1; locked-benefit teasers and the upgrade path |
| Patron    | `patron@pierpaddock.demo`    | $9,500   | Crest 2; progress bar toward Collector, quarterly report |
| Collector | `collector@pierpaddock.demo` | $40,000  | Crest 3; Vault price tracking, Retailer's Credit, grail list |
| Curator   | `curator@pierpaddock.demo`   | $110,000 | Crest 4; a members-only first-look piece in the Vault |
| Steward   | `steward@pierpaddock.demo`   | $260,000 | Crest 5; named concierge, by-invitation badge, a matched grail |

- Staff / admin surfaces:
  - **Operator Console** (`/console/`) — the **operator** account runs the Crest
    loyalty program (members, simulate-purchase, analytics, config).
  - **Merchant Portal** (`/merchant/`) — the **merchant** account manages their
    own listings, XML feed and sales. See the section below.
  - **Wagtail CMS admin** (`/cms-admin/`) — authors and publishes the **Lifestyle
    magazine** (articles, categories, authors, images, ad zones, snippets). Sign in as
    the dedicated **magazine editor** (`editor@pierpaddock.demo` — in the Editors +
    Moderators groups, CMS-only) or the **admin** superuser.
  - **Django admin** (`/admin/`) and the **Oscar dashboard** (`/dashboard/`) — the
    store's low-level + catalogue/order back offices.
- The **admin** superuser reaches everything (`/admin/`, `/dashboard/`, `/cms-admin/`,
  console, portal); create your own with `./bin/python manage.py createsuperuser`.
- All accounts above ship in the committed `db.sqlite3`. If you rebuild from scratch,
  `load_loyalty_demo` recreates the five tier members, the operator **and the merchant**,
  and `load_lifestyle_demo` recreates the **magazine editor**.

---

## Project layout

```
config/                 Django project (settings, urls, wsgi)
apps/
  core/                 Brand context processors, homepage view,
                        load_demo_catalogue command, image generator, template tags
  shop/                 Faceted product-browse view (the main shop page)
  loyalty/              Crest membership: models, services, Operator Console,
                        SendGrid/Mailchimp email layer (inactive), load_loyalty_demo
                        (also seeds the operator + merchant accounts)
  merchant/             Merchant Portal: MerchantProfile (Partner + XML feed),
                        supplier-scoped listings / feed / sales views
  vault/                Investment-tracking vault (MarketValue/Valuation, VaultItem)
  compare/              Session-based watch comparison
  lifestyle/            Wagtail magazine: page models (index/category/article/author),
                        StreamField blocks, ad zones + sponsored-product snippets,
                        RSS/Atom feeds, JSON-LD/SEO (seo.py), robots/llms (discovery.py),
                        /advertise/ + subscribe + search views, seed commands
  checkout/             Forked Oscar checkout — payments disabled at place-order
  shipping/             Forked Oscar shipping — two named insured methods
  blog/                 Legacy blog / journal — superseded by lifestyle (/blog/* → /lifestyle/*)
  pages/                About / FAQ / Contact / custom 404 (magazine-skinned under /lifestyle/)
templates/              Theme-skinned overrides of Oscar templates + custom pages
                        (incl. templates/loyalty/, templates/console/, templates/merchant/;
                        magazine templates live in apps/lifestyle/templates/lifestyle/)
static/                 Theme assets + brand CSS (css/pierpaddock.css, css/loyalty.css,
                        css/console.css, css/partner.css) + crest favicon (img/crest.ico);
                        the magazine skin is under apps/lifestyle/static/lifestyle/
media/                  Product imagery + Wagtail magazine originals (original_images/) and
                        committed renditions (images/); sorl thumbnail cache is gitignored
```

### Brand configuration (single source of truth)
`config/settings.py`:

```python
BRAND_NAME = "Pier & Paddock"           # ← change me to re-brand everywhere
BRAND_TAGLINE = "Time, well spent."
```



---

## Magazine Ad Inventory Positioning

**Pier & Paddock is a marketplace and media destination for the harbor-and-grid set:
collectors who acquire rather than shop. We put our partners on our shelves and in our
pages.**

That sentence is the merchant pitch, and it is also the spec for the advertising layer.
Two revenue paths, one audience:

- **The shelves** — the commission-only marketplace. Merchant-fulfilled inventory, no
  listing fees, P&P owns the customer relationship, CRM, and marketing.
- **The pages** — the Lifestyle magazine (`/lifestyle/`). Ad zones, banners, and
  sponsored products, sold to the same partner merchants and to adjacent luxury brands.

The magazine is not a content-marketing appendage to the shop. It is the acquisition
engine *and* an inventory of its own: it gathers the audience, and then it sells access
to that audience alongside the products in the shop.

### What partners are buying

Access to a curated audience — not reach, not impressions at a competitive CPM. The
audience is the moat. Do not build, name, or sell any placement in a way that implies
P&P competes on cost against performance channels. P&P is not the cheaper way to reach
collectors. It is the only way.

**Never in partner-facing copy, ad-product names, or the media kit:** discount framing,
CPM/CPC comparisons, "affordable," "cost-effective," "cheaper than," "efficient spend,"
"prohibitively expensive elsewhere." Price is a second-conversation topic, never a
first-slide one.

### What this means for the Revive Ad Server integration

- **Placements are editorial, not interruptive.** Ad zones sit within the reading
  experience of the magazine at a density that a luxury reader tolerates. If a zone
  makes `/lifestyle/` feel like an ad-supported content farm, it is the wrong zone,
  regardless of what it earns.
- **Name zones for the room, not the pixel dimensions.** Partner-facing zone names
  should read as placements in a magazine (e.g. *Feature Lead*, *Section Sponsor*,
  *Between the Lines*, *Back Page*), even where the internal Revive zone IDs are
  conventional IAB sizes. The internal implementation can be standard; the sold product
  should not sound standard.
- **Every advertiser is a partner or a peer.** No remnant inventory, no ad networks, no
  programmatic backfill. An unsold zone renders as house inventory promoting P&P shop
  products, Crest membership, or an editorial feature — never as a filler ad from an
  exchange. An empty zone is better than an off-brand one.
- **Sponsored products connect the two paths.** Sponsored placements in the magazine
  should link into the shop where the merchant has listed inventory, so an editorial
  read converts into an acquisition without leaving the property.
- **Frequency and targeting serve the reader.** Revive's targeting exists here to make
  a placement more relevant to a collector, not to maximize impressions per session.

### Brand voice guardrails (applies to all ad and editorial copy)

- Pillar line: *Curation · Provenance · Signature Service*
- Taglines: *Time, well spent.* · *Purveyors of the exceptional.* · *From the harbor to
  the grid.*
- Approved register: *"Some things are not bought. They are acquired."*
- Rejected register: anything price-adjacent, discount-framing, or aspirational in a
  mass-market way.

---

## Out of scope (by design)

Real payment processing, real inventory sync, and live market pricing. Email is
**built but inactive**: the loyalty layer is structured for SendGrid (transactional)
and Mailchimp (marketing), but makes no network calls in the demo — transactional
"sends" fall back to the console backend and marketing "syncs" are logged no-ops.
Add real keys and flip `LOYALTY_TRANSACTIONAL_ENABLED` / `LOYALTY_MARKETING_ENABLED`
to activate. The magazine's **Revive Adserver** ad slots and **Mailchimp** newsletter
are likewise inactive seams (placeholder creatives; sign-ups stored locally as
`PendingSubscriber`), and `GA4_MEASUREMENT_ID`, `INDEXNOW_KEY` and
`LIFESTYLE_OG_DEFAULT_IMAGE` are empty config placeholders. This is a local/demo-host
build for showing off the storefront, the magazine and the UX.
