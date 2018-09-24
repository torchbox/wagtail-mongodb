from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.vary import vary_on_headers
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns

from mongodb_blog.esi import views as esi_views
from mongodb_blog.search import views as search_views
from mongodb_blog.utils.cache import get_default_cache_control_decorator
from mongodb_blog.utils.views import favicon, robots

# Private URLs are not meant to be cached.
private_urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # Search cache-control headers are set on the view itself.
    path('search/', search_views.search, name='search'),
]


# Public URLs that are meant to be cached.
urlpatterns = [
    path('esi/<name>/', esi_views.esi, name='esi'),
    path('sitemap.xml', sitemap),
    path('favicon.ico', favicon),
    path('robots.txt', robots),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        # Add views for testing 404 and 500 templates
        path('test404/', TemplateView.as_view(template_name='404.html')),
        path('test500/', TemplateView.as_view(template_name='500.html')),
    ]

if settings.DEBUG or settings.ENABLE_STYLEGUIDE:
    urlpatterns += [
        # Add styleguide
        path('styleguide/', TemplateView.as_view(template_name='styleguide.html')),
    ]

# Set public URLs to use the "default" cache settings.
urlpatterns = decorate_urlpatterns(urlpatterns,
                                   get_default_cache_control_decorator())

# Set vary header to instruct cache to serve different version on different
# cookies, different request method (e.g. AJAX) and different protocol
# (http vs https).
urlpatterns = decorate_urlpatterns(
    urlpatterns,
    vary_on_headers('Cookie', 'X-Requested-With', 'X-Forwarded-Proto',
                    'Accept-Encoding')
)

# Join private and public URLs.
urlpatterns = private_urlpatterns + urlpatterns + [
    # Add Wagtail URLs at the end.
    # Wagtail cache-control is set on the page models's serve methods.
    path('', include(wagtail_urls)),
]
