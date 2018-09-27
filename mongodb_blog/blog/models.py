from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.functions import Coalesce
from django.utils.text import slugify
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import StreamField
from wagtail.search import index

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

    categories = ParentalManyToManyField(
        'blog.Category',
        related_name='blog_posts',
    )

    search_fields = BasePage.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body')
    ]

    content_panels = BasePage.content_panels + [
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
        posts = (
            BlogPage.objects
            .live()
            .public()
            .descendant_of(self)
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

    @route(r'^category/(?P<category>[\w-]+)/$')
    def category(self, request, category):
        # TODO: Implement
        return super().serve(request)


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

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)