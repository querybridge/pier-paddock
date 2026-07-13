"""Fictional dummy catalogue data for the demo store.

All reference numbers, prices and specs are illustrative only. Prices are in
USD. ``stock`` of 0 marks an item as "Sold".
"""

# Keys: brand, model, ref, price, material, size, movement, dial, bracelet,
# water, condition, year, box_papers, collections, stock, reviews(optional)

WATCHES = [
    # ---------------- Rolex (14) ----------------
    dict(brand="Rolex", model="Submariner Date", ref="126610LN", price=14250,
         material="Stainless Steel", size="41 mm", movement="Automatic, Cal. 3235",
         dial="Black", bracelet="Oyster Steel", water="300 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=2,
         reviews=[
             ("The reference dive watch", "Nothing else feels this solid on the wrist. The 3235 movement keeps superb time and the bracelet is faultless.", 5, "James W."),
             ("Worth the wait", "Arrived fully insured and exactly as described. Box and papers all present.", 5, "Marcus T."),
         ]),
    dict(brand="Rolex", model="Submariner (No Date)", ref="124060", price=11600,
         material="Stainless Steel", size="41 mm", movement="Automatic, Cal. 3230",
         dial="Black", bracelet="Oyster Steel", water="300 m",
         condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Rolex", model="GMT-Master II 'Pepsi'", ref="126710BLRO", price=23800,
         material="Stainless Steel", size="40 mm", movement="Automatic, Cal. 3285",
         dial="Black", bracelet="Jubilee Steel", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Rolex", model="GMT-Master II 'Batman'", ref="126710BLNR", price=19900,
         material="Stainless Steel", size="40 mm", movement="Automatic, Cal. 3285",
         dial="Black", bracelet="Oyster Steel", water="100 m",
         condition="Unworn", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=2),
    dict(brand="Rolex", model="Cosmograph Daytona", ref="116500LN", price=34500,
         material="Stainless Steel", size="40 mm", movement="Automatic, Cal. 4130",
         dial="White", bracelet="Oyster Steel", water="100 m",
         condition="Pre-Owned Excellent", year=2021, box_papers="Full Set",
         collections=["Sports", "Chronographs"], stock=0),
    dict(brand="Rolex", model="Datejust 41", ref="126334", price=11200,
         material="Stainless Steel", size="41 mm", movement="Automatic, Cal. 3235",
         dial="Blue", bracelet="Jubilee Steel", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),
    dict(brand="Rolex", model="Day-Date 40", ref="228238", price=42500,
         material="Yellow Gold", size="40 mm", movement="Automatic, Cal. 3255",
         dial="Champagne", bracelet="President Gold", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=1),
    dict(brand="Rolex", model="Explorer II", ref="226570", price=12400,
         material="Stainless Steel", size="42 mm", movement="Automatic, Cal. 3285",
         dial="White", bracelet="Oyster Steel", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=2),
    dict(brand="Rolex", model="Sea-Dweller", ref="126600", price=16800,
         material="Stainless Steel", size="43 mm", movement="Automatic, Cal. 3235",
         dial="Black", bracelet="Oyster Steel", water="1220 m",
         condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Rolex", model="Oyster Perpetual 41", ref="124300", price=6400,
         material="Stainless Steel", size="41 mm", movement="Automatic, Cal. 3230",
         dial="Blue", bracelet="Oyster Steel", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),
    dict(brand="Rolex", model="Oyster Perpetual 36", ref="126000", price=5900,
         material="Stainless Steel", size="36 mm", movement="Automatic, Cal. 3230",
         dial="Green", bracelet="Oyster Steel", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),
    dict(brand="Rolex", model="Datejust 36", ref="126234", price=9400,
         material="Stainless Steel", size="36 mm", movement="Automatic, Cal. 3235",
         dial="Silver", bracelet="Oyster Steel", water="100 m",
         condition="Pre-Owned Excellent", year=2020, box_papers="Watch Only",
         collections=["Dress", "Pre-Owned"], stock=1),
    dict(brand="Rolex", model="Sky-Dweller", ref="336934", price=17200,
         material="Stainless Steel", size="42 mm", movement="Automatic, Cal. 9002",
         dial="Blue", bracelet="Oyster Steel", water="100 m",
         condition="Unworn", year=2023, box_papers="Full Set",
         collections=["Complications"], stock=1),
    dict(brand="Rolex", model="Yacht-Master 40", ref="126622", price=14600,
         material="Two-Tone", size="40 mm", movement="Automatic, Cal. 3235",
         dial="Slate", bracelet="Oyster Steel", water="100 m",
         condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),

    # ---------------- Audemars Piguet (8) ----------------
    dict(brand="Audemars Piguet", model="Royal Oak 15500ST", ref="15500ST.OO.1220ST.01",
         price=46000, material="Stainless Steel", size="41 mm",
         movement="Automatic, Cal. 4302", dial="Blue", bracelet="Steel Bracelet",
         water="50 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1,
         reviews=[
             ("The 'Jumbo' feel in 41mm", "The Grande Tapisserie dial catches light unbelievably. Bracelet integration is on another level.", 5, "Daniel R."),
             ("Impeccable service", "IDC fulfilment was seamless — insured overnight and the watch is mint.", 5, "Priya S."),
         ]),
    dict(brand="Audemars Piguet", model="Royal Oak 15500ST Black", ref="15500ST.OO.1220ST.03",
         price=44500, material="Stainless Steel", size="41 mm",
         movement="Automatic, Cal. 4302", dial="Black", bracelet="Steel Bracelet",
         water="50 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Audemars Piguet", model="Royal Oak Chronograph", ref="26331ST.OO.1220ST.02",
         price=62000, material="Stainless Steel", size="41 mm",
         movement="Automatic, Cal. 2385", dial="Blue", bracelet="Steel Bracelet",
         water="50 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Chronographs", "Sports"], stock=1),
    dict(brand="Audemars Piguet", model="Royal Oak Offshore Chronograph", ref="26420SO.OO.A002CA.01",
         price=49000, material="Ceramic", size="43 mm",
         movement="Automatic, Cal. 4404", dial="Blue", bracelet="Rubber Strap",
         water="100 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Chronographs", "Sports"], stock=1),
    dict(brand="Audemars Piguet", model="Royal Oak Jumbo Extra-Thin", ref="16202ST.OO.1240ST.01",
         price=98000, material="Stainless Steel", size="39 mm",
         movement="Automatic, Cal. 7121", dial="Blue", bracelet="Steel Bracelet",
         water="50 m", condition="Unworn", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=0),
    dict(brand="Audemars Piguet", model="Royal Oak 15510ST", ref="15510ST.OO.1320ST.07",
         price=48000, material="Stainless Steel", size="41 mm",
         movement="Automatic, Cal. 4302", dial="Silver", bracelet="Steel Bracelet",
         water="50 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Audemars Piguet", model="Royal Oak Offshore Diver", ref="15720ST.OO.A027CA.01",
         price=42500, material="Stainless Steel", size="42 mm",
         movement="Automatic, Cal. 4308", dial="Green", bracelet="Rubber Strap",
         water="300 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Audemars Piguet", model="Royal Oak Frosted Gold", ref="15454BC.GG.1259BC.03",
         price=78000, material="White Gold", size="37 mm",
         movement="Automatic, Cal. 5135", dial="Silver", bracelet="White Gold Bracelet",
         water="50 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Dress", "Complications"], stock=1),

    # ---------------- Patek Philippe (8) ----------------
    dict(brand="Patek Philippe", model="Nautilus 5711/1A", ref="5711/1A-010",
         price=128000, material="Stainless Steel", size="40 mm",
         movement="Automatic, Cal. 26-330 S C", dial="Blue", bracelet="Steel Bracelet",
         water="120 m", condition="Pre-Owned Excellent", year=2021, box_papers="Full Set",
         collections=["Sports"], stock=1,
         reviews=[
             ("Grail acquired", "Discontinued and impossible to find. The blue dial gradient is mesmerising in person.", 5, "Alexander P."),
             ("Flawless example", "Crisp edges, full set, and the concierge team verified everything before shipping.", 5, "Helena V."),
             ("Investment grade", "Pre-owned but indistinguishable from new. Superb.", 4, "Tobias L."),
         ]),
    dict(brand="Patek Philippe", model="Nautilus 5811/1G", ref="5811/1G-001",
         price=148000, material="White Gold", size="41 mm",
         movement="Automatic, Cal. 26-330 S C", dial="Blue", bracelet="White Gold Bracelet",
         water="120 m", condition="Unworn", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Patek Philippe", model="Aquanaut 5167A", ref="5167A-001",
         price=53000, material="Stainless Steel", size="40 mm",
         movement="Automatic, Cal. 324 S C", dial="Black", bracelet="Rubber Strap",
         water="120 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Patek Philippe", model="Aquanaut 5168G", ref="5168G-001",
         price=72000, material="White Gold", size="42 mm",
         movement="Automatic, Cal. 324 S C", dial="Blue", bracelet="Rubber Strap",
         water="120 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Patek Philippe", model="Calatrava 6119G", ref="6119G-001",
         price=38500, material="White Gold", size="39 mm",
         movement="Manual, Cal. 30-255 PS", dial="Silver", bracelet="Leather Strap",
         water="30 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=1),
    dict(brand="Patek Philippe", model="Calatrava 5227G", ref="5227G-010",
         price=41000, material="White Gold", size="39 mm",
         movement="Automatic, Cal. 324 S C", dial="White", bracelet="Leather Strap",
         water="30 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Dress"], stock=1),
    dict(brand="Patek Philippe", model="Annual Calendar 5396G", ref="5396G-014",
         price=58000, material="White Gold", size="38.5 mm",
         movement="Automatic, Cal. 324 S QA", dial="Blue", bracelet="Leather Strap",
         water="30 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Complications"], stock=1),
    dict(brand="Patek Philippe", model="Twenty~4 Automatic", ref="7300/1200A-011",
         price=42000, material="Stainless Steel", size="36 mm",
         movement="Automatic, Cal. 324 S C", dial="Silver", bracelet="Steel Bracelet",
         water="60 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=1),

    # ---------------- Omega (6) ----------------
    dict(brand="Omega", model="Speedmaster Professional Moonwatch", ref="310.30.42.50.01.001",
         price=7300, material="Stainless Steel", size="42 mm",
         movement="Manual, Cal. 3861", dial="Black", bracelet="Steel Bracelet",
         water="50 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Chronographs"], stock=2,
         reviews=[
             ("The Moonwatch, perfected", "The 3861 Master Chronometer upgrade makes a legend even better. Hesalite version wears beautifully.", 5, "Neil G."),
             ("Best value in luxury", "Iconic history, in-house movement, and a price that makes sense. Insured shipping was quick.", 5, "Sofia M."),
         ]),
    dict(brand="Omega", model="Seamaster Diver 300M", ref="210.30.42.20.01.001",
         price=5700, material="Stainless Steel", size="42 mm",
         movement="Automatic, Cal. 8800", dial="Blue", bracelet="Steel Bracelet",
         water="300 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=2),
    dict(brand="Omega", model="Seamaster Aqua Terra 150M", ref="220.10.41.21.03.001",
         price=6000, material="Stainless Steel", size="41 mm",
         movement="Automatic, Cal. 8900", dial="Blue", bracelet="Steel Bracelet",
         water="150 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),
    dict(brand="Omega", model="Seamaster Planet Ocean 600M", ref="215.30.44.21.01.001",
         price=6900, material="Stainless Steel", size="43.5 mm",
         movement="Automatic, Cal. 8900", dial="Black", bracelet="Steel Bracelet",
         water="600 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Omega", model="Speedmaster '57 Co-Axial", ref="332.10.41.51.02.002",
         price=9200, material="Stainless Steel", size="40.5 mm",
         movement="Manual, Cal. 9906", dial="Blue", bracelet="Steel Bracelet",
         water="50 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Chronographs"], stock=1),
    dict(brand="Omega", model="Constellation 39mm", ref="131.30.39.20.06.001",
         price=5500, material="Stainless Steel", size="39 mm",
         movement="Automatic, Cal. 8900", dial="Grey", bracelet="Steel Bracelet",
         water="100 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),

    # ---------------- Cartier (5) ----------------
    dict(brand="Cartier", model="Santos de Cartier Large", ref="WSSA0018",
         price=7500, material="Stainless Steel", size="39.8 mm",
         movement="Automatic, Cal. 1847 MC", dial="Silver", bracelet="Steel Bracelet",
         water="100 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),
    dict(brand="Cartier", model="Santos-Dumont", ref="WSSA0022",
         price=6900, material="Stainless Steel", size="38 mm",
         movement="Quartz", dial="Silver", bracelet="Leather Strap",
         water="30 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=1),
    dict(brand="Cartier", model="Tank Must Large", ref="WSTA0041",
         price=3300, material="Stainless Steel", size="33.7 mm",
         movement="Quartz", dial="Silver", bracelet="Leather Strap",
         water="30 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=2),
    dict(brand="Cartier", model="Ballon Bleu 40mm", ref="WSBB0039",
         price=7000, material="Stainless Steel", size="40 mm",
         movement="Automatic, Cal. 1847 MC", dial="Silver", bracelet="Steel Bracelet",
         water="30 m", condition="Pre-Owned Excellent", year=2020, box_papers="Watch Only",
         collections=["Dress", "Pre-Owned"], stock=0),
    dict(brand="Cartier", model="Tank Française", ref="WSTA0074",
         price=8300, material="Stainless Steel", size="32 mm",
         movement="Automatic, Cal. 1847 MC", dial="Silver", bracelet="Steel Bracelet",
         water="30 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=1),

    # ---------------- Vacheron Constantin (4) ----------------
    dict(brand="Vacheron Constantin", model="Overseas Self-Winding", ref="4500V/110A-B128",
         price=32500, material="Stainless Steel", size="41 mm",
         movement="Automatic, Cal. 5100", dial="Blue", bracelet="Steel Bracelet",
         water="150 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports"], stock=1),
    dict(brand="Vacheron Constantin", model="Overseas Chronograph", ref="5500V/110A-B148",
         price=41500, material="Stainless Steel", size="42.5 mm",
         movement="Automatic, Cal. 5200", dial="Blue", bracelet="Steel Bracelet",
         water="150 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Chronographs", "Sports"], stock=1),
    dict(brand="Vacheron Constantin", model="Patrimony Self-Winding", ref="4100U/000G-B464",
         price=28000, material="White Gold", size="40 mm",
         movement="Automatic, Cal. 2450 Q6", dial="Silver", bracelet="Leather Strap",
         water="30 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Dress"], stock=1),
    dict(brand="Vacheron Constantin", model="Traditionnelle Manual", ref="82172/000P-9888",
         price=39000, material="Platinum", size="38 mm",
         movement="Manual, Cal. 4400 AS", dial="Slate", bracelet="Leather Strap",
         water="30 m", condition="Unworn", year=2022, box_papers="Full Set",
         collections=["Complications", "Dress"], stock=1),

    # ---------------- Richard Mille (3) ----------------
    dict(brand="Richard Mille", model="RM 011 Felipe Massa", ref="RM011",
         price=188000, material="Titanium", size="50 mm",
         movement="Automatic, Cal. RMAC3", dial="Black", bracelet="Rubber Strap",
         water="50 m", condition="Pre-Owned Excellent", year=2019, box_papers="Full Set",
         collections=["Chronographs", "Sports"], stock=1,
         reviews=[
             ("Engineering as art", "Skeletonised flyback chronograph that weighs nothing. Wears like a piece of motorsport history.", 5, "Lewis F."),
             ("Statement piece", "Photos don't do the case architecture justice. Full set, fully insured delivery.", 5, "Omar K."),
         ]),
    dict(brand="Richard Mille", model="RM 035 Rafael Nadal", ref="RM035",
         price=168000, material="Titanium", size="49 mm",
         movement="Manual, Cal. RMUL3", dial="Grey", bracelet="Rubber Strap",
         water="50 m", condition="Pre-Owned Excellent", year=2020, box_papers="Watch Only",
         collections=["Sports", "Pre-Owned"], stock=0),
    dict(brand="Richard Mille", model="RM 030 Declutchable Rotor", ref="RM030",
         price=142000, material="Titanium", size="50 mm",
         movement="Automatic, Cal. RMAR2", dial="Black", bracelet="Rubber Strap",
         water="50 m", condition="Unworn", year=2021, box_papers="Full Set",
         collections=["Complications"], stock=1),

    # ---------------- IWC / Jaeger-LeCoultre (2) ----------------
    dict(brand="IWC", model="Big Pilot's Watch Perpetual Calendar", ref="IW329602",
         price=52000, material="Rose Gold", size="46.5 mm",
         movement="Automatic, Cal. 52615", dial="Green", bracelet="Green Calfskin Strap",
         water="60 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Complications"], stock=2,
         # Primary + on-rollover product photos.
         images=["product/iwc1.png", "product/iwc2.png"]),
    dict(brand="Rolex", model="Cosmograph Daytona", ref="126500LN",
         price=38000, material="Stainless Steel", size="40 mm",
         movement="Automatic, Cal. 4131", dial="White", bracelet="Oyster Steel",
         water="100 m", condition="New", year=2023, box_papers="Full Set",
         collections=["Sports", "Chronographs"], stock=1,
         # Primary + on-rollover product photos.
         images=["product/daytona-126500ln-1.jpg", "product/daytona-126500ln-2.jpg"]),
    # F.P. Journe — an independent grail (also the Steward's matched grail piece).
    dict(brand="F.P. Journe", model="Chronomètre Bleu", ref="CB", price=55000,
         material="Tantalum", size="39 mm", movement="Manual wind, Cal. 1304",
         dial="Chrome Blue", bracelet="Alligator Leather", water="30 m",
         condition="Pre-Owned Excellent", year=2022, box_papers="Full Set",
         collections=["Dress"], stock=1,
         reviews=[
             ("The independent grail", "The chrome-blue dial is mesmerising in the metal, and the tantalum case has a depth stainless never will. Worth every year on the waitlist.", 5, "Henry S."),
         ]),
]


BRANDS = [
    "Rolex", "Audemars Piguet", "Patek Philippe", "Omega", "Cartier",
    "Vacheron Constantin", "Richard Mille", "IWC", "Jaeger-LeCoultre",
]

COLLECTIONS = ["Sports", "Dress", "Chronographs", "Complications", "Pre-Owned"]


BLOG_POSTS = [
    dict(
        title="How to Buy Your First Luxury Watch",
        author="The Editors",
        excerpt="A practical guide to making a confident first purchase — from "
                "setting a budget to understanding box and papers.",
        body=(
            "Buying your first luxury watch should be exciting, not intimidating. "
            "Start by deciding how you'll wear it: a steel sports watch is endlessly "
            "versatile, while a slim dress watch shines under a cuff.\n\n"
            "Set a realistic budget and remember that condition and completeness "
            "matter enormously. A 'Full Set' — watch, box, warranty card and booklets "
            "— holds value far better than a watch sold on its own.\n\n"
            "Finally, buy from a source you trust. Every timepiece in our collection is "
            "independently authenticated and delivered fully insured with signature "
            "service — so your first watch arrives exactly as promised."
        ),
        days_ago=6,
    ),
    dict(
        title="Submariner vs. Seamaster: Which Dive Watch Wins?",
        author="The Editors",
        excerpt="Two icons of the deep, compared head to head on heritage, "
                "movement, and everyday wearability.",
        body=(
            "The Rolex Submariner and Omega Seamaster Diver 300M are the two most "
            "recognisable dive watches in the world — and choosing between them is "
            "largely a matter of character.\n\n"
            "The Submariner is the archetype: understated, supremely robust, and a "
            "byword for quiet luxury. The Seamaster answers with its wave dial, helium "
            "escape valve and a co-axial movement that punches well above its price.\n\n"
            "You can't go wrong with either. If you favour resale strength and timeless "
            "restraint, the Submariner leads. If you want more watch for the money and a "
            "touch of flair, the Seamaster is unbeatable value."
        ),
        days_ago=14,
    ),
    dict(
        title="Why Box & Papers Matter",
        author="The Editors",
        excerpt="The little cardboard box and folded warranty card can be worth "
                "thousands. Here's why collectors obsess over completeness.",
        body=(
            "In the pre-owned market, two identical watches can carry very different "
            "prices for one reason: box and papers.\n\n"
            "The 'papers' — a dated, stamped warranty card — confirm provenance and "
            "the year of sale. The original box, booklets and accessories complete the "
            "'Full Set'. Collectors prize this completeness because it signals a watch "
            "that has been cared for and is far easier to resell.\n\n"
            "Every listing in our store clearly states its box-and-papers status, and "
            "our authentication partners verify each item before it ships."
        ),
        days_ago=24,
    ),
    dict(
        title="The Integrated Bracelet Sports Watch, Explained",
        author="The Editors",
        excerpt="From the Royal Oak to the Nautilus, the luxury sports watch defines "
                "modern collecting. A short history.",
        body=(
            "In 1972, Gérald Genta sketched a stainless-steel watch with an octagonal "
            "bezel and an integrated bracelet. The Audemars Piguet Royal Oak was born — "
            "and it redefined what luxury could look like.\n\n"
            "Patek Philippe followed with the Nautilus in 1976, and Vacheron Constantin "
            "later joined with the Overseas. Today these integrated-bracelet sports "
            "watches are among the most sought-after timepieces in the world.\n\n"
            "Their appeal is simple: one watch that looks equally right with a wetsuit "
            "or a tuxedo, finished to a standard once reserved for dress watches alone."
        ),
        days_ago=33,
    ),
]
