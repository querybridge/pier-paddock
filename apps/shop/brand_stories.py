"""Short brand stories shown on the PDP (below "About this piece") and used to enrich
the Product schema's Brand node.

Copy is **original editorial prose** — founding year and headquarters are factual (not
copyrightable); the positioning line is our own wording, deliberately NOT any brand's
trademarked slogan or marketing copy, to avoid copyright/trademark conflicts.
"""

# brand name (as stored in the product 'brand' attribute) -> story text.
BRAND_STORIES = {
    "Rolex": (
        "Founded in 1905 and headquartered in Geneva, Switzerland, Rolex is a byword for "
        "precision and prestige. Its tool watches and classics alike are built to be worn "
        "hard, kept for a lifetime, and handed on to the next generation."
    ),
    "Audemars Piguet": (
        "Founded in 1875 in Le Brassus, Switzerland, Audemars Piguet is one of the last great "
        "watch houses still in the hands of its founding families. It helped define the luxury "
        "sports watch and remains a benchmark for daring design and hand-finishing."
    ),
    "Patek Philippe": (
        "Founded in 1839 and based in Geneva, Switzerland, Patek Philippe is widely regarded as "
        "the finest of the traditional Geneva houses. It is prized for its complications, "
        "meticulous finishing, and timepieces made to be passed down through generations."
    ),
    "Omega": (
        "Founded in 1848 and headquartered in Biel/Bienne, Switzerland, Omega is a pioneer of "
        "precision timekeeping — official timekeeper of the Olympic Games and the first watch "
        "worn on the Moon — pairing serious engineering with everyday wearability."
    ),
    "Cartier": (
        "Founded in 1847 in Paris, France, Cartier is as celebrated for jewellery as for "
        "watchmaking. Defined by shape and elegance, it is the house that helped turn the "
        "wristwatch into an object of design."
    ),
    "Vacheron Constantin": (
        "Founded in 1755 in Geneva, Switzerland, Vacheron Constantin is the oldest watch "
        "manufacturer in continuous operation. It unites more than two and a half centuries of "
        "craft with the decorative artistry of its métiers d'art."
    ),
    "Richard Mille": (
        "Founded in 2001 in Les Breuleux, Switzerland, Richard Mille is a modern disruptor of "
        "haute horlogerie. It builds featherweight, shock-resistant watches from aerospace "
        "materials — engineering-first pieces designed to be worn anywhere."
    ),
    "IWC": (
        "Founded in 1868 in Schaffhausen, Switzerland, the International Watch Company (IWC) "
        "married American manufacturing ideas with Swiss craft. It is known for robust, "
        "understated engineering and a celebrated line of pilot's watches."
    ),
    "Jaeger-LeCoultre": (
        "Founded in 1833 in Le Sentier, Switzerland, Jaeger-LeCoultre is often called the "
        "watchmaker's watchmaker. It has produced hundreds of in-house calibres and inventions, "
        "from the reversible Reverso to some of horology's most complex movements."
    ),
    "F.P. Journe": (
        "Founded in 1999 in Geneva, Switzerland, F.P. Journe is among the most collectable "
        "independents of the modern era. The work of a single master watchmaker, it is known "
        "for inventive movements and quietly radical design."
    ),
}


def get_brand_story(brand):
    """Return {'brand', 'text'} for a brand name, or None. Case-insensitive."""
    if not brand:
        return None
    brand = str(brand).strip()
    text = BRAND_STORIES.get(brand)
    if text is None:
        for name, t in BRAND_STORIES.items():
            if name.lower() == brand.lower():
                brand, text = name, t
                break
    return {"brand": brand, "text": text} if text else None
