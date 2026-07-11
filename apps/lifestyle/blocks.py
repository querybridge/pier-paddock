"""StreamField blocks for the article body (Phase 3).

Each block renders via a template under templates/lifestyle/blocks/. The product
card and inline-ad blocks are the seams to the shop and the ad server.
"""
from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

RICH_FEATURES = ["bold", "italic", "link", "ol", "ul", "h3", "h4", "hr", "blockquote"]


class PullQuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    attribution = blocks.CharBlock(required=False)

    class Meta:
        template = "lifestyle/blocks/pull_quote.html"
        icon = "openquote"
        label = "Pull quote"


class FullBleedImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt = blocks.CharBlock(help_text="Alt text (required for accessibility & SEO).")
    caption = blocks.CharBlock(required=False)
    credit = blocks.CharBlock(required=False)

    class Meta:
        template = "lifestyle/blocks/full_bleed_image.html"
        icon = "image"
        label = "Full-bleed image"


class GalleryItemBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt = blocks.CharBlock()
    caption = blocks.CharBlock(required=False)


class GalleryBlock(blocks.StructBlock):
    images = blocks.ListBlock(GalleryItemBlock())

    class Meta:
        template = "lifestyle/blocks/gallery.html"
        icon = "image"
        label = "Image gallery"


class ProductCardBlock(blocks.StructBlock):
    """Shoppable Oscar product — image, name, 'View at Pier & Paddock'. Never a
    price-led CTA (brand rule)."""
    product_id = blocks.IntegerBlock(help_text="Oscar product ID (the number in a /catalogue/…_<id>/ URL).")
    blurb = blocks.CharBlock(required=False, help_text="One-line hook.")

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context)
        from oscar.core.loading import get_model
        Product = get_model("catalogue", "Product")
        ctx["product"] = Product.objects.filter(id=value.get("product_id")).first()
        return ctx

    class Meta:
        template = "lifestyle/blocks/product_card.html"
        icon = "pick"
        label = "Product card"


class FAQItemBlock(blocks.StructBlock):
    question = blocks.CharBlock()
    answer = blocks.RichTextBlock(features=RICH_FEATURES)


class FAQBlock(blocks.StructBlock):
    items = blocks.ListBlock(FAQItemBlock())

    class Meta:
        template = "lifestyle/blocks/faq.html"
        icon = "help"
        label = "FAQ"


class KeyTakeawaysBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, default="Key takeaways")
    points = blocks.ListBlock(blocks.CharBlock())

    class Meta:
        template = "lifestyle/blocks/key_takeaways.html"
        icon = "list-ul"
        label = "Key takeaways"


class InlineAdBlock(blocks.StructBlock):
    zone = blocks.ChoiceBlock(choices=[
        ("in_content", "In-content leaderboard"),
        ("leaderboard_top", "Leaderboard"),
        ("footer", "Footer"),
    ], default="in_content")

    class Meta:
        template = "lifestyle/blocks/inline_ad.html"
        icon = "placeholder"
        label = "Ad slot"


class ArticleBodyBlock(blocks.StreamBlock):
    """The article body block set."""
    paragraph = blocks.RichTextBlock(features=RICH_FEATURES, label="Rich text")
    pull_quote = PullQuoteBlock()
    image = FullBleedImageBlock()
    gallery = GalleryBlock()
    video = EmbedBlock(label="Video (YouTube/Vimeo)", icon="media",
                       template="lifestyle/blocks/video.html")
    product = ProductCardBlock()
    faq = FAQBlock()
    key_takeaways = KeyTakeawaysBlock()
    table = blocks.RawHTMLBlock(label="Table (HTML)", icon="table",
                                template="lifestyle/blocks/table.html")
    divider = blocks.StaticBlock(admin_text="— divider —", label="Divider",
                                 icon="horizontalrule", template="lifestyle/blocks/divider.html")
    inline_ad = InlineAdBlock()

    class Meta:
        block_counts = {}
