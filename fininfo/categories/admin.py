from typing import Any

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.text import slugify
from parler.admin import TranslatableAdmin
from parler.utils.context import switch_language

from fininfo.categories.models import Category
from fininfo.utils.transliterate import to_latin


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, TranslatableAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "is_menu",
                ),
            },
        ),
    )
    list_display = ["name", "category_order"]
    ordering = ["category_order"]
    exclude = ["slug"]
    readonly_fields = ["slug"]

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not obj.id:
            if obj.get_current_language() == "uz-cyril":
                name = to_latin(obj.name)
                description = to_latin(obj.description)
                with switch_language(obj, "uz"):
                    obj.name = name
                    obj.slug = slugify(name, allow_unicode=True)
                    obj.description = description
                    obj.save()
        return super().save_model(request, obj, form, change)
