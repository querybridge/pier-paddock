"""Single source of truth for the Crest membership ladder.

Tier *names* and the *benefits* unlocked at each crest level live here so that
templates, the customer dashboard, the operator console and the seed command
all describe the program identically. The dollar *thresholds* that drive crest
calculation are intentionally NOT hardcoded here — they live in the editable
``ProgramConfig`` model (see ``models.py``) so the demo can show the bands are
tunable. ``tiers.py`` only owns presentation + the crest->name mapping.
"""

# Crest count -> tier name. Crest count is the canonical level (1..5); the name
# is derived from it. Keep this mapping and the benefit table below in lockstep.
TIER_NAMES = {
    0: "Guest",      # no account / not opted in — shown as zero filled crests
    1: "Member",
    2: "Patron",
    3: "Collector",
    4: "Curator",
    5: "Steward",
}

MAX_CRESTS = 5

# Concierge access scales with tier. Stored on Membership.concierge_channel.
CONCIERGE_NONE = "none"
CONCIERGE_EMAIL = "email"          # Patron: shared concierge inbox
CONCIERGE_DEDICATED = "dedicated"  # Curator: named dedicated channel
CONCIERGE_DIRECT = "direct"        # Steward: personal advisor, direct line
CONCIERGE_CHOICES = (
    (CONCIERGE_NONE, "No concierge"),
    (CONCIERGE_EMAIL, "Email concierge"),
    (CONCIERGE_DEDICATED, "Dedicated channel"),
    (CONCIERGE_DIRECT, "Direct line"),
)

# Which concierge channel each crest level grants.
CONCIERGE_BY_CREST = {
    0: CONCIERGE_NONE,
    1: CONCIERGE_NONE,
    2: CONCIERGE_EMAIL,
    3: CONCIERGE_EMAIL,
    4: CONCIERGE_DEDICATED,
    5: CONCIERGE_DIRECT,
}

# Benefits unlocked at each crest level. ``crest`` is the level at which the
# benefit first becomes available; the dashboard shows everything at or below
# the member's level as unlocked and everything above as a dimmed teaser.
# ``key`` lets views/templates reference a benefit without matching on prose.
BENEFITS = [
    {"crest": 1, "key": "vault_save", "label": "Unlimited Vault",
     "blurb": "Save and organise any number of watches."},
    {"crest": 1, "key": "newsletter", "label": "Market newsletter",
     "blurb": "Our regular read on the secondary market."},
    {"crest": 2, "key": "early_access_24", "label": "24-hour early access",
     "blurb": "First look at new drops, a day before public listing."},
    {"crest": 2, "key": "alerts", "label": "Restock & price alerts",
     "blurb": "Be told the moment a piece returns or moves on price."},
    {"crest": 2, "key": "concierge_email", "label": "Email concierge",
     "blurb": "A dedicated inbox for sourcing questions."},
    {"crest": 2, "key": "quarterly_report", "label": "Quarterly market report",
     "blurb": "Our analysts' quarterly briefing, delivered to you."},
    {"crest": 3, "key": "price_tracking", "label": "Vault price tracking",
     "blurb": "Live secondary values and portfolio total in your Vault."},
    {"crest": 3, "key": "retailers_credit", "label": "Retailer's Credit",
     "blurb": "Store credit, funded by us, toward your next acquisition."},
    {"crest": 3, "key": "grail_list", "label": "Grail list",
     "blurb": "Tell us the pieces you're hunting; we'll watch for them."},
    {"crest": 3, "key": "first_alert", "label": "Collectors' first-alert list",
     "blurb": "Priority notification ahead of the general list."},
    {"crest": 4, "key": "first_look_72", "label": "72-hour private first-look",
     "blurb": "New pieces appear in your Vault before they're listed."},
    {"crest": 4, "key": "reserve_hold", "label": "Reserve & hold",
     "blurb": "Place a hold on a piece while you decide."},
    {"crest": 4, "key": "priority_sourcing", "label": "Priority sourcing",
     "blurb": "Your sourcing requests move to the front of the queue."},
    {"crest": 5, "key": "personal_concierge", "label": "Personal concierge",
     "blurb": "A named advisor on a direct line."},
    {"crest": 5, "key": "trade_in_terms", "label": "Top trade-in terms",
     "blurb": "Our most favourable trade-in valuations."},
    {"crest": 5, "key": "grail_priority", "label": "Grail priority",
     "blurb": "First right of refusal on matched grails."},
    {"crest": 5, "key": "marquee_invitations", "label": "Marquee invitations",
     "blurb": "Invitations to our by-invitation events and previews."},
]


def tier_name(crest_count):
    return TIER_NAMES.get(int(crest_count or 0), TIER_NAMES[0])


def concierge_for(crest_count):
    return CONCIERGE_BY_CREST.get(int(crest_count or 0), CONCIERGE_NONE)


def benefits_with_state(crest_count):
    """Return the full benefit list, each annotated ``unlocked``/``unlocks_at``
    for the given crest level — drives the dashboard benefits panel."""
    crest_count = int(crest_count or 0)
    rows = []
    for b in BENEFITS:
        rows.append({
            **b,
            "unlocked": crest_count >= b["crest"],
            "unlocks_at": tier_name(b["crest"]),
        })
    return rows
