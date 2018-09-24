from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup,
                                                modeladmin_register)

from mongodb_blog.news.models import NewsType


class NewsTypeModelAdmin(ModelAdmin):
    model = NewsType
    menu_icon = 'tag'


class TaxonomiesModelAdminGroup(ModelAdminGroup):
    menu_label = "Taxonomies"
    items = (
        NewsTypeModelAdmin,
    )
    menu_icon = 'tag'


modeladmin_register(TaxonomiesModelAdminGroup)
