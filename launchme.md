# Launching the Pier & Paddock demo on PythonAnywhere

Step-by-step guide to get this Django + django-oscar demo running at
`https://<your-username>.pythonanywhere.com`.

Throughout, replace **`USERNAME`** with your PythonAnywhere username.

> The repo ships a populated `db.sqlite3` and product imagery, so the demo runs
> with its data already in place — no reseed required.

---

## 1. Open a Bash console

PythonAnywhere dashboard → **Consoles** → **Bash**.

## 2. Clone the repository

```bash
cd ~
git clone https://github.com/querybridge/pier-paddock.git
cd pier-paddock
```

## 3. Create a virtualenv and install dependencies

The committed venv is gitignored, so create a fresh one (PythonAnywhere has
virtualenvwrapper preinstalled):

```bash
mkvirtualenv --python=python3.10 pier-paddock
pip install -r requirements.txt
```

This creates the venv at `/home/USERNAME/.virtualenvs/pier-paddock`.
(`workon pier-paddock` reactivates it in future consoles.)

## 4. Prepare the database & static files

```bash
python manage.py migrate              # no-op if already migrated; safe to run
python manage.py collectstatic --noinput
```

Optional — rebuild the demo catalogue/imagery/accounts from scratch:

```bash
python manage.py load_demo_catalogue
python manage.py load_loyalty_demo   # Crest membership: per-tier members + data
```

(The shipped `db.sqlite3` already includes the membership data, so this is only
needed if you rebuild from scratch. `load_loyalty_demo` is idempotent.)

## 5. Create the web app

Dashboard → **Web** → **Add a new web app** →
**Manual configuration** (NOT the Django quick-start) → **Python 3.10**.

## 6. Configure the Web tab

In the **Web** tab set:

| Field | Value |
|-------|-------|
| **Source code** | `/home/USERNAME/pier-paddock` |
| **Working directory** | `/home/USERNAME/pier-paddock` |
| **Virtualenv** | `/home/USERNAME/.virtualenvs/pier-paddock` (or just `pier-paddock`) |

Then click the **WSGI configuration file** link and replace its entire contents
with:

```python
import os
import sys

path = "/home/USERNAME/pier-paddock"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

# Production-style demo settings (see config/settings.py)
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_ALLOWED_HOSTS"] = "USERNAME.pythonanywhere.com"
os.environ["DJANGO_SECRET_KEY"] = "replace-with-a-long-random-string"
# CSRF for *.pythonanywhere.com is already trusted by default; override only if needed:
# os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "https://USERNAME.pythonanywhere.com"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Generate a secret key (run in the Bash console):

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 7. Add static & media file mappings

Still in the **Web** tab, under **Static files**, add two mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/USERNAME/pier-paddock/staticfiles` |
| `/media/`  | `/home/USERNAME/pier-paddock/media` |

These let PythonAnywhere serve the theme/CSS/JS and the product images directly.

## 8. Reload

Click the green **Reload** button at the top of the Web tab, then visit:

```
https://USERNAME.pythonanywhere.com
```

---

## Demo accounts

| Role            | Email               | Password     | Where |
|-----------------|---------------------|--------------|-------|
| Customer        | `demo@example.com`  | `Demo1234!`  | the storefront (cart, Vault, orders) |
| Admin/dashboard | `admin@example.com` | `Admin1234!` | `/dashboard/` and `/admin/` |

(Both exist in the committed database. Change the admin password after launch, or
create your own with `python manage.py createsuperuser`.)

---

## Updating the live demo later

Run these in a **PythonAnywhere Bash console**, then click **Reload** in the Web tab.

```bash
cd ~/pier-paddock

# 1. Pull the latest main. Discard the live DB's runtime churn first, or the
#    pull will conflict on db.sqlite3 (it's modified as the site runs).
git checkout -- db.sqlite3
git checkout main
git pull                                   # FULL pull — gets settings.py changes too

# 2. Sanity-check the settings actually updated (a partial checkout that misses
#    config/settings.py causes "model … isn't in an application in INSTALLED_APPS")
grep -n "apps.merchant" config/settings.py

# 3. Virtualenv + dependencies
workon pier-paddock
pip install -r requirements.txt            # no-op if deps unchanged; safe

# 4. Database, static files, thumbnails
python manage.py migrate                   # applies any new app tables (no-op if the shipped DB has them)
python manage.py collectstatic --noinput   # picks up new/changed CSS, JS and the crest favicon
python manage.py thumbnail clear           # clear the thumbnail cache so images regenerate
python manage.py check                     # should report "no issues"
```

Then **Reload** the web app (Web tab → green button — this loads new
settings/middleware), and **hard-refresh** your browser (Cmd/Ctrl+Shift+R), since
browsers cache CSS and broken images.

> **Why each step matters:** `git checkout -- db.sqlite3` avoids the pull
> conflict; the full `git pull` (not a partial `git checkout <files>`) ensures
> `config/settings.py` is updated; `migrate` adds any new app tables;
> `collectstatic` is required whenever CSS/JS changed; `thumbnail clear` fixes
> "missing images on shop/home" after the cache or DB changed.

---

## Troubleshooting

- **Site loads but is unstyled** → the `/static/` mapping is wrong, or you didn't
  run `collectstatic`. Re-check step 7 and re-run step 4, then Reload.
- **Product images broken on the shop / home pages but fine on product detail**
  → stale thumbnail cache. The listing/home cards use sorl-thumbnail (the
  `media/cache/` thumbnails are gitignored). Clear the cache so they regenerate:
  ```bash
  workon pier-paddock && python manage.py thumbnail clear
  ```
  Then **Reload** and load the shop page once (the thumbnails are built on first
  request). The product-detail page uses the original images, which is why it
  works either way.
- **Broken product images** → the `/media/` mapping is wrong; it must point to
  `/home/USERNAME/pier-paddock/media`.
- **`Model class … isn't in an application in INSTALLED_APPS`** (e.g.
  `MerchantProfile`) → `config/settings.py` is stale, so the app isn't
  registered. This happens after a partial `git checkout <files>` that skipped
  settings. Fix with a full pull (or `git checkout main -- config/settings.py`),
  clear stale bytecode, and Reload:
  ```bash
  git checkout main -- config/settings.py
  find . -path '*/apps/*' -name __pycache__ -exec rm -rf {} +
  ```
- **CSRF "Forbidden" on login / add-to-cart / checkout** → make sure
  `DJANGO_ALLOWED_HOSTS` in the WSGI file is your real domain. CSRF already trusts
  `https://*.pythonanywhere.com` by default.
- **`DisallowedHost`** → same fix: set `DJANGO_ALLOWED_HOSTS` to
  `USERNAME.pythonanywhere.com` (or `*` for any host).
- **Disk quota (free tier ≈ 512 MB)** → venv (~280 MB) + repo (~25 MB) +
  `staticfiles/` (~15 MB) ≈ 320 MB. It fits, but if you hit the quota, remove the
  thumbnail cache with `rm -rf media/cache` (it regenerates on demand).
- **Errors check** → run `python manage.py check --deploy` for security warnings,
  and the server **Error log** (Web tab) for tracebacks.

### Quickest possible demo (skip the static mappings)

For a throwaway look, set `os.environ["DJANGO_DEBUG"] = "True"` in the WSGI file
and skip step 7 — Django will serve `/static/` and `/media/` itself. Fine for a
quick low-traffic demo, but **not** recommended for anything public, since
`DEBUG=True` exposes tracebacks. Use the proper setup above for a stakeholder demo.
