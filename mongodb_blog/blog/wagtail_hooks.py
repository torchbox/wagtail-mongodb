from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Category


@modeladmin_register
class CategoryModelAdmin(ModelAdmin):
    model = Category
    menu_icon = 'folder'
    list_display = ('name', 'slug')
