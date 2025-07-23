from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from fininfo.ads.models import Ad
from fininfo.ads.models import AdType


class AdAdminInline(admin.StackedInline):
    extra = 2
    model = Ad


@admin.register(AdType)
class AdTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("Turi"),
            {
                "fields": (
                    "name",
                    "width",
                    "height",
                    "slug",
                ),
            },
        ),
    )
    list_display = ["name", "slug"]
    inlines = [AdAdminInline]
    prepopulated_fields = {"slug": ("name",)}
