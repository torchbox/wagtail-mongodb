from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailcodeblock.blocks import CodeBlock


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()

    class Meta:
        icon = "image"
        template = "blocks/image_block.html"


class DocumentBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        template = "blocks/document_block.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(classname="full")
    attribution = blocks.CharBlock(required=False)
    image = ImageChooserBlock()

    class Meta:
        icon = "openquote"
        template = "blocks/quote_block.html"


# Main streamfield block to be inherited by Pages
class StoryBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(classname="full title", icon='title')
    paragraph = blocks.RichTextBlock(
        features=[
            'bold', 'italic',
            'ul', 'ol', 'hr',
            'link', 'document-link'
        ],
    )
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock()
    call_to_action = SnippetChooserBlock(
        'utils.CallToActionSnippet',
        template="blocks/call_to_action_block.html"
    )
    document = DocumentBlock()
    code = CodeBlock()

    class Meta:
        template = "blocks/stream_block.html"
