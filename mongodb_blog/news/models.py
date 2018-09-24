from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.functions import Coalesce
from django.utils.text import slugify
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.search import index

from mongodb_blog.utils.blocks import StoryBlock
from mongodb_blog.utils.models import BasePage, RelatedPage


class NewsType(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class NewsPageNewsType(models.Model):
    page = ParentalKey(
        'news.NewsPage',
        related_name='news_types'
    )
    news_type = models.ForeignKey(
        'NewsType',
        related_name='+',
        on_delete=models.CASCADE
    )

    panels = [
        FieldPanel('news_type')
    ]

    def __str__(self):
        return self.news_type.title


class NewsPageRelatedPage(RelatedPage):
    source_page = ParentalKey(
        'news.NewsPage',
        related_name='related_pages'
    )


class NewsPage(BasePage):
    # It's datetime for easy comparison with first_published_at
    publication_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Use this field to override the date that the "
        "news item appears to have been published."
    )
    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock())

    categories = ParentalManyToManyField(
        'news.Category',
        related_name='news_pages',
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
        InlinePanel('news_types', label="News types"),
        InlinePanel('related_pages', label="Related pages"),
    ]

    subpage_types = []
    parent_page_types = ['NewsIndex']

    @property
    def display_date(self):
        if self.publication_date:
            return self.publication_date
        else:
            return self.first_published_at


class NewsIndex(BasePage):
    subpage_types = ['NewsPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request, *args, **kwargs):
        news = NewsPage.objects.live().public().descendant_of(self).annotate(
            date=Coalesce('publication_date', 'first_published_at')
        ).order_by('-date')

        if request.GET.get('news_type'):
            news = news.filter(news_types__news_type=request.GET.get('news_type'))

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(news, settings.DEFAULT_PER_PAGE)
        try:
            news = paginator.page(page)
        except PageNotAnInteger:
            news = paginator.page(1)
        except EmptyPage:
            news = paginator.page(paginator.num_pages)

        context = super().get_context(request, *args, **kwargs)
        context.update(
            news=news,
            # Only show news types that have been used
            news_types=NewsPageNewsType.objects.all().values_list(
                'news_type__pk', 'news_type__title'
            ).distinct().order_by('news_type__title')
        )
        return context


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
