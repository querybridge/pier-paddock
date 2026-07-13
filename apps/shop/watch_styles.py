"""Watch style classification + PDP styling snippets (per WATCH_STYLE_GUIDE.md).

Each catalogue watch maps to ONE of the twelve house styles, derived from its title
(brand + model) so there's no stored attribute to keep in sync. The matching snippet is
shown on the PDP ("Pier & Paddock Styling"); the style keys drive the Shop nav + browse
filter. Snippet copy is taken verbatim from the in-repo style guide.
"""

# key, label, PDP snippet (from WATCH_STYLE_GUIDE.md — one paragraph each).
STYLES = [
    ("dress", "Dress",
     "This is your evening watch — reserved for the occasions that ask for a jacket, if "
     "not a tie. It slips beneath a shirt cuff and speaks only when glanced at, which is "
     "precisely the point. Pairs naturally with black tie, formal business dress, and any "
     "room where restraint reads as confidence."),
    ("sports-dive", "Sports / Dive",
     "This is your everywhere watch — equally at home on the dock rail at sunrise and "
     "across the dinner table that evening. It carries genuine capability without "
     "announcing it, and it moves from swim shorts to a blazer without a change of strap. "
     "Pairs well with resort wear, weekend tailoring, and business casual when the meeting "
     "is yours to run."),
    ("chronograph", "Chronograph",
     "This is your watch for the days you intend to win — a driver's instrument at heart, "
     "with the pushers and registers to prove it. It brings visible purpose to the wrist "
     "and suits the man who keeps score. Pairs well with paddock casual, weekend tailoring, "
     "and office professional attire when worn on a bracelet."),
    ("racing-motorsport", "Racing / Motorsport",
     "This is your grid-walk watch — a piece with competition in its bloodline, made to be "
     "read at a glance the way a driver reads a pit board. It belongs at the circuit, the "
     "concours lawn, and the Cars & Coffee where the conversation starts at the wrist. "
     "Pairs well with paddock casual, driving jackets, and sharp weekend attire."),
    ("regatta-yachting", "Regatta / Yachting",
     "This is your watch for the water — built around the countdown to a start line, and "
     "entirely at ease long after the finish gun. It carries the regatta in its dial and "
     "the clubhouse in its manner. Pairs well with sailing kit, resort tailoring, and the "
     "navy blazer that never quite leaves the coast."),
    ("gmt-travel", "GMT / Travel",
     "This is your travel watch — one glance covers home and away, which is exactly the "
     "rhythm of a life lived across time zones. It moves through airports, boardrooms, and "
     "harbors without ever asking to be reset. Pairs well with travel tailoring, business "
     "casual, and office professional attire alike."),
    ("pilot-aviation", "Pilot / Aviation",
     "This is your watch for clear intentions — an aviator's instrument that puts "
     "legibility above all else and wears its heritage plainly. It brings a squared-away "
     "confidence to casual and weekend attire, and holds its own under a field jacket or a "
     "well-cut bomber. Pairs well with smart casual through business casual."),
    ("field-explorer", "Field / Explorer",
     "This is your watch for the days without a schedule — compact, legible, and utterly "
     "dependable, whether the terrain is a trail, a tarmac, or a Saturday errand. It "
     "carries no pretense, which is its own kind of polish. Pairs well with casual and "
     "outdoor attire, and slips comfortably under a chore coat or field jacket."),
    ("integrated-sports-luxury", "Integrated-Bracelet Sports Luxury",
     "This is your statement of arrival — a sports watch finished to the standard of a "
     "dress piece, and the silhouette that defines the modern collection. It carries "
     "executive presence into every room and needs no second piece to back it up. Pairs "
     "seamlessly with office professional attire, evening tailoring, and the open-collar "
     "confidence in between."),
    ("dress-sport", "Dress-Sport / Everyday Executive",
     "This is your office watch — creating executive presence from the first handshake, "
     "and equally correct across business casual through office professional attire. It is "
     "the piece that anchors a working wardrobe: dressed enough for the boardroom, capable "
     "enough for everything after five. If a collection has a cornerstone, this is it."),
    ("complication", "Complication / Haute Horlogerie",
     "This is your collector's watch — a piece acquired for the mechanism as much as the "
     "moment, and worn where craftsmanship is the language of the room. It rewards the "
     "second look and the third. Pairs with formal and evening attire, and with any "
     "setting where the company appreciates what is on the wrist."),
    ("heritage", "Heritage / Vintage-Inspired",
     "This is your watch with a backstory — a design that earned its shape decades ago and "
     "wears that history lightly. It brings warmth and character to tailoring that leans "
     "classic, and it photographs like it has always been on your wrist. Pairs well with "
     "heritage casual, tweed-and-knit tailoring, and business casual with a soft shoulder."),
]

STYLE_LABEL = {k: l for k, l, _ in STYLES}
STYLE_SNIPPET = {k: s for k, _, s in STYLES}
STYLE_ORDER = [k for k, _, _ in STYLES]


def classify(title):
    """Return the style key for a product title (brand + model). Title-only so it needs
    no DB/attribute access. Order matters — most specific identity first."""
    t = (title or "").lower()

    def has(*words):
        return any(w in t for w in words)

    if has("gmt-master", "gmt master", " gmt"):
        return "gmt-travel"
    if has("explorer"):
        return "field-explorer"
    if has("pilot", "flieger", "navitimer"):
        return "pilot-aviation"
    if has("sky-dweller", "perpetual calendar", "annual calendar", "tourbillon",
           "minute repeater", "skeleton", "declutchable", "grande complication",
           "quantième", "moon phase"):
        return "complication"
    if has("daytona"):
        return "racing-motorsport"
    if "richard mille" in t:
        return "racing-motorsport"
    if has("speedmaster"):
        return "heritage" if has("'57", "57 co-axial", " '57") else "chronograph"
    if has("submariner", "sea-dweller", "seamaster diver", "planet ocean",
           "fifty fathoms", "aquastar"):
        return "sports-dive"
    if has("yacht-master", "regatta", "yachtmaster"):
        return "sports-dive"
    if has("royal oak", "nautilus", "aquanaut", "overseas", "laureato", "octo"):
        return "integrated-sports-luxury"
    if has("aqua terra", "constellation", "datejust", "oyster perpetual", "twenty~4",
           "twenty-4", "santos de cartier"):
        return "dress-sport"
    if has("day-date"):
        return "dress"
    if has("calatrava", "patrimony", "traditionnelle", "tank", "ballon", "chronomètre",
           "chronometre", "santos-dumont", "portofino", "reverso", "saxonia", "1815"):
        return "dress"
    if has("chronograph", "chrono"):
        return "chronograph"
    return "dress-sport"


# ── Oscar option attribute ("style") — managed in the dashboard / merchant form ──
STYLE_GROUP_NAME = "Watch Style"


def all_styles():
    """[(key, label)] for all twelve styles — for the add-listing dropdown."""
    return [(k, l) for k, l, _ in STYLES]


def ensure_style_attribute():
    """Idempotently create the AttributeOptionGroup + options + the 'style' option
    ProductAttribute on the Watch class. Returns the option group."""
    from oscar.core.loading import get_model

    ProductClass = get_model("catalogue", "ProductClass")
    ProductAttribute = get_model("catalogue", "ProductAttribute")
    AttributeOptionGroup = get_model("catalogue", "AttributeOptionGroup")
    AttributeOption = get_model("catalogue", "AttributeOption")

    group, _ = AttributeOptionGroup.objects.get_or_create(name=STYLE_GROUP_NAME)
    for key, label, _ in STYLES:
        AttributeOption.objects.update_or_create(
            group=group, code=key, defaults={"option": label})

    pc = ProductClass.objects.get(name="Watch")
    attr, _ = ProductAttribute.objects.get_or_create(
        product_class=pc, code="style",
        defaults={"name": "Style", "type": "option",
                  "option_group": group, "required": False})
    if attr.type != "option" or attr.option_group_id != group.id:
        attr.name, attr.type, attr.option_group, attr.required = "Style", "option", group, False
        attr.save()
    return group


def _option_for_key(key):
    from oscar.core.loading import get_model

    AttributeOption = get_model("catalogue", "AttributeOption")
    return AttributeOption.objects.filter(group__name=STYLE_GROUP_NAME, code=key).first()


def set_product_style(product, key):
    """Set the product's style option (creates the attribute infra if missing)."""
    opt = _option_for_key(key) or (ensure_style_attribute() and _option_for_key(key))
    if opt is not None:
        product.attr.style = opt
        product.attr.save()


def product_style(product):
    """(key, label, snippet) from the stored `style` option; classify() as fallback."""
    key = None
    try:
        opt = product.attr.style
        key = getattr(opt, "code", None)
    except Exception:
        key = None
    if not key or key not in STYLE_SNIPPET:
        key = classify(product.title)
    return key, STYLE_LABEL[key], STYLE_SNIPPET[key]


def styles_present():
    """Ordered [(key, label)] for styles with ≥1 browsable product (stored value;
    classify() fallback before the attribute is populated)."""
    from oscar.core.loading import get_model

    Product = get_model("catalogue", "Product")
    PAV = get_model("catalogue", "ProductAttributeValue")
    codes = {c for c in PAV.objects.filter(
        attribute__code="style", product__in=Product.objects.browsable()
    ).values_list("value_option__code", flat=True) if c}
    if not codes:
        codes = {classify(t) for t in
                 Product.objects.browsable().values_list("title", flat=True)}
    return [(k, STYLE_LABEL[k]) for k in STYLE_ORDER if k in codes]


def ids_for_style(style_key):
    """Browsable product IDs with the given style (stored value; classify() fallback)."""
    from oscar.core.loading import get_model

    PAV = get_model("catalogue", "ProductAttributeValue")
    ids = list(PAV.objects.filter(
        attribute__code="style", value_option__code=style_key
    ).values_list("product_id", flat=True))
    if ids:
        return ids
    Product = get_model("catalogue", "Product")
    return [pid for pid, title in
            Product.objects.browsable().values_list("id", "title")
            if classify(title) == style_key]
