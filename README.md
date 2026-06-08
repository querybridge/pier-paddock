# Pier & Paddock — Luxury Watch Demo Store

A polished **demo ecommerce store** for high-end watches, built with
**Django + django-oscar** and skinned with the "zwat" theme.

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
  and the latest journal posts.
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
- **Cart & checkout** — fully navigable multi-step checkout (shipping address →
  shipping method → payment → preview) with the **payment step disabled** and a
  clear "payments are disabled in this demo" notice. Two named shipping methods
  (complimentary insured overnight, or paid Saturday delivery).
- **Accounts** — registration, login, profile, order history and address book.
- **Content** — About, FAQ and Contact pages (contact posts to the console email
  backend), a simple blog/journal, and a custom 404.

---

## Tech stack

| Concern   | Choice |
|-----------|--------|
| Framework | Django 5.2 + django-oscar 4.1 |
| Database  | SQLite (`db.sqlite3`) |
| Images    | Pillow — generated placeholder imagery; sorl-thumbnail for thumbnails |
| Search    | Haystack simple backend; faceted shop filtering via a custom ORM view |
| Custom apps | `loyalty` (Crest membership + Operator Console), `vault` (investment tracking), `compare`, `shop` (faceted browse), `blog`, `pages`, plus forked `checkout` (payments disabled) and `shipping` (named methods) |
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
(`/account/grail/`), the alerts/notification feed (`/account/alerts/`), and the
public marketing page at `/membership/`.

**Operator Console** (`/console/`, staff-only — a branded-clean back-office UI):
analytics (tier mix, **Retailer's Credit liability**, grail demand), a member list
+ detail with clearly-labelled **demo controls** (Simulate purchase, set spend,
grant credit, issue invitation, mark grail matched), inventory early-access
flagging, and program configuration.

> **Demo flow:** log in as each tier to show the experience, then open the
> Operator Console, pick the **Patron**, hit **Simulate purchase** on a ~$20K
> watch, and watch them advance to **Collector** live with credit accrued.

---

## Demo accounts

| Role            | Email                | Password    |
|-----------------|----------------------|-------------|
| Customer        | `demo@example.com`   | `Demo1234!` |
| Admin / Console | `admin@example.com`  | `Admin1234!`|

**Crest membership — one member per tier** (shared password `Crest1234!`):

| Tier | Email |
|------|-------|
| Member    | `member@pierpaddock.demo` |
| Patron    | `patron@pierpaddock.demo` |
| Collector | `collector@pierpaddock.demo` |
| Curator   | `curator@pierpaddock.demo` |
| Steward   | `steward@pierpaddock.demo` |

- The **customer** account is for the shopper experience (vault, orders, addresses).
- The **admin** account reaches the Oscar dashboard at `/dashboard/`, Django admin
  at `/admin/`, and the **Operator Console** at `/console/` (any staff user).
  Create your own with `./bin/python manage.py createsuperuser`.

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
  vault/                Investment-tracking vault (MarketValue/Valuation, VaultItem)
  compare/              Session-based watch comparison
  checkout/             Forked Oscar checkout — payments disabled at place-order
  shipping/             Forked Oscar shipping — two named insured methods
  blog/                 Simple blog / journal
  pages/                About / FAQ / Contact / custom 404
templates/              Theme-skinned overrides of Oscar templates + custom pages
static/                 Theme assets + brand CSS (css/pierpaddock.css)
media/                  Product & blog imagery (thumbnail cache is gitignored)
```

### Brand configuration (single source of truth)
`config/settings.py`:

```python
BRAND_NAME = "Pier & Paddock"           # ← change me to re-brand everywhere
BRAND_TAGLINE = "Time, well spent."
```

---

## Out of scope (by design)

Real payment processing, real inventory sync, and live market pricing. Email is
**built but inactive**: the loyalty layer is structured for SendGrid (transactional)
and Mailchimp (marketing), but makes no network calls in the demo — transactional
"sends" fall back to the console backend and marketing "syncs" are logged no-ops.
Add real keys and flip `LOYALTY_TRANSACTIONAL_ENABLED` / `LOYALTY_MARKETING_ENABLED`
to activate. This is a local/demo-host build for showing off the storefront and UX.
