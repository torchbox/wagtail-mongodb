from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.functions import Coalesce
from django.http import Http404
from django.utils.text import slugify
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from mongodb_blog.utils.blocks import StoryBlock
from mongodb_blog.utils.models import BasePage


class BlogPage(BasePage):
    # It's datetime for easy comparison with first_published_at
    publication_date = models.DateTimeField(
        null=True, blank=True,
        help_text=(
            "Use this field to override the date that the blog post appears "
            "to have been published."
        )
    )
    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock())
    author = models.ForeignKey(
        'blog.Author',
        on_delete=models.PROTECT,
        related_name='blog_posts',
    )

    categories = ParentalManyToManyField(
        'blog.Category',
        related_name='blog_posts',
    )

    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body')
    ]

    content_panels = BasePage.content_panels + [
        SnippetChooserPanel('author'),
        FieldPanel('publication_date'),
        FieldPanel('introduction'),
        StreamFieldPanel('body'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
    ]

    subpage_types = []
    parent_page_types = ['blog.BlogIndex']

    @property
    def display_date(self):
        if self.publication_date:
            return self.publication_date
        else:
            return self.first_published_at


class BlogIndex(RoutablePageMixin, BasePage):
    subpage_types = ['blog.BlogPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request, *args, **kwargs):
        filter_kwargs = {}

        if self.category:
            filter_kwargs['categories'] = self.category

        if self.author:
            filter_kwargs['author'] = self.author

        posts = (
            BlogPage.objects
            .live()
            .public()
            .descendant_of(self)
            .filter(**filter_kwargs)
            .annotate(date=Coalesce('publication_date', 'first_published_at'))
            .order_by('-date')
        )

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, settings.DEFAULT_PER_PAGE)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = super().get_context(request, *args, **kwargs)
        context['posts'] = posts
        return context

    def serve(self, *args, **kwargs):
        self.category = kwargs.pop('category', None)
        self.author = kwargs.pop('author', None)

        return super().serve(*args, **kwargs)

    @route(r'^category/(?P<category>[\w-]+)/$')
    def category(self, request, category):
        try:
            category = Category.objects.get(slug=category)
        except Category.DoesNotExist:
            raise Http404
        return self.serve(request, category=category)

    @route(r'^author/(?P<author>[\w-]+)/$')
    def author(self, request, author):
        try:
            author = Author.objects.get(slug=author)
        except Author.DoesNotExist:
            raise Http404
        return self.serve(request, author=author)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        blank=True,
        max_length=255,
        help_text=(
            "Populated from name if not populated. Note: Changing this will "
            "change the tag taxonomy URL."
        ),
    )

    panels = [
        FieldPanel('name', classname="full title"),
        FieldPanel('slug'),
    ]

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Populate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


@register_snippet
class Author(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ForeignKey(
        'images.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    slug = models.SlugField(
        blank=True,
        max_length=255,
        help_text=(
            "Populated from name if not populated. Note: Changing this will "
            "change the author taxonomy URL."
        ),
    )

    panels = [
        FieldPanel('name', classname="full title"),
        ImageChooserPanel('photo'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Populate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
