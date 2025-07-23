from django.contrib import admin
from parler.admin import TranslatableAdmin

from fininfo.pages.models import Page


@admin.register(Page)
class NewsAdmin(TranslatableAdmin):
    list_display = ["name"]
